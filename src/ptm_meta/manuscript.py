"""Generate Typst data payload and compile the CoSE synthesis manuscript PDF."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from ptm_meta.analysis import wilson_ci


def prepare_manuscript_data(repo_root: Path) -> dict[str, Any]:
    """Assemble live summary statistics and ML metrics for manuscript/ptm_manuscript.typ."""
    reports = pd.read_parquet(repo_root / "data/processed/reports.parquet")
    arms = pd.read_parquet(repo_root / "data/processed/trial_arms.parquet")
    ml_path = repo_root / "data/processed/ml_metrics.json"
    ml = json.loads(ml_path.read_text(encoding="utf-8")) if ml_path.exists() else {}

    pdfs = reports[reports["has_pdf"]].copy()
    trt = arms[~arms["is_control"]].copy()

    # Season breakdown
    season_rows: list[dict[str, Any]] = []
    for (_order, season), grp in reports.groupby(["season_order", "season"]):
        season_rows.append(
            {
                "season": str(season),
                "total_awards": int(len(grp)),
                "pdf_reports": int(grp["has_pdf"].sum()),
                "main_pdfs": int(((grp["track"] == "main") & grp["has_pdf"]).sum()),
                "junior_pdfs": int(((grp["track"] == "junior") & grp["has_pdf"]).sum()),
            }
        )
    season_rows.sort(key=lambda r: r["season"])

    # Amendment outcome breakdown
    amend_rows: list[dict[str, Any]] = []
    scored_trt = trt[trt["outcome_vs_regolith_control"].isin(["improved", "neutral", "reduced"])]
    for cat, grp in scored_trt.groupby("amendment_category"):
        n_tot = len(grp)
        n_imp = int((grp["outcome_vs_regolith_control"] == "improved").sum())
        p, lo, hi = wilson_ci(n_imp, n_tot)
        amend_rows.append(
            {
                "category": str(cat).replace("_", " "),
                "n_arms": int(n_tot),
                "n_improved": n_imp,
                "improved_pct": round(p * 100.0, 1),
                "ci_low": round(lo * 100.0, 1),
                "ci_high": round(hi * 100.0, 1),
            }
        )
    amend_rows.sort(key=lambda r: (-r["n_arms"], -r["improved_pct"]))

    # Bottlenecks
    bn_counts: dict[str, int] = {}
    for raw in pdfs["primary_bottlenecks"].dropna():
        for tag in str(raw).split(";"):
            t = tag.strip()
            if t:
                bn_counts[t] = bn_counts.get(t, 0) + 1
    top_bottlenecks = [
        {"bottleneck": k.replace("_", " "), "count": v, "pct": round(100.0 * v / max(1, len(pdfs)), 1)}
        for k, v in sorted(bn_counts.items(), key=lambda x: -x[1])[:8]
    ]

    data = {
        "total_award_entries": int(len(reports)),
        "total_pdf_reports": int(len(pdfs)),
        "total_pages": int(pdfs["page_count"].fillna(0).sum()),
        "total_tables": int(pdfs["table_count"].fillna(0).sum()),
        "total_arms": int(len(arms)),
        "total_treatment_arms": int(len(trt)),
        "n_states": int(reports["location_state"].dropna().nunique()),
        "ncbitaxon_mapped": int(pdfs["crop_ncbitaxon"].notna().sum()),
        "earth_ctrl_pct": round(100.0 * float(pdfs["has_earth_soil_control"].fillna(False).mean()), 1),
        "reg_ctrl_pct": round(100.0 * float(pdfs["has_unamended_regolith_control"].fillna(False).mean()), 1),
        "stat_test_pct": round(100.0 * float(pdfs["has_statistical_test"].fillna(False).mean()), 1),
        "celestial_counts": {str(k): int(v) for k, v in pdfs["celestial_body"].value_counts().items()},
        "top_crops": [
            {"crop": str(k), "count": int(v)}
            for k, v in pdfs["crop_common_name"].value_counts().head(8).items()
        ],
        "amendment_outcomes": amend_rows[:10],
        "top_bottlenecks": top_bottlenecks,
        "ml": ml,
        "figures_present": {
            f"fig{i}": (repo_root / f"manuscript/figures/fig{i}.png").exists()
            for i in range(1, 5)
        },
    }
    out_json = repo_root / "manuscript/manuscript_data.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def compile_manuscript_pdf(repo_root: Path) -> Path:
    """Compile manuscript/ptm_manuscript.typ via Typst into static PDF targets."""
    prepare_manuscript_data(repo_root)
    typ_src = repo_root / "manuscript/ptm_manuscript.typ"
    if not typ_src.exists():
        raise FileNotFoundError(f"Missing Typst source: {typ_src}")

    typst_bin = shutil.which("typst") or "/opt/homebrew/bin/typst"
    out_manuscript = repo_root / "manuscript/Plant_the_Moon_Meta_Analysis.pdf"
    out_static = repo_root / "book/_static/manuscript/Plant_the_Moon_Meta_Analysis.pdf"
    out_static.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [typst_bin, "compile", "--root", str(repo_root), str(typ_src), str(out_manuscript)],
        check=True,
    )
    shutil.copy2(out_manuscript, out_static)
    return out_static
