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
    n_pdfs = max(1, len(pdfs))

    # Chronological season breakdown
    season_rows: list[dict[str, Any]] = []
    for (order, season), grp in reports.groupby(["season_order", "season"]):
        season_rows.append(
            {
                "order": int(order),
                "season": str(season),
                "total_awards": int(len(grp)),
                "pdf_reports": int(grp["has_pdf"].sum()),
                "main_pdfs": int(((grp["track"] == "main") & grp["has_pdf"]).sum()),
                "junior_pdfs": int(((grp["track"] == "junior") & grp["has_pdf"]).sum()),
                "meta_only": int((~grp["has_pdf"]).sum()),
            }
        )
    season_rows.sort(key=lambda r: r["order"])

    # Division-level experimental rigor breakdown
    division_rows: list[dict[str, Any]] = []
    for div, grp in pdfs.groupby("division_norm"):
        division_rows.append(
            {
                "division": str(div),
                "n_pdfs": int(len(grp)),
                "mean_pages": round(float(grp["page_count"].fillna(0).mean()), 1),
                "mean_tables": round(float(grp["table_count"].fillna(0).mean()), 1),
                "earth_ctrl_pct": round(100.0 * float(grp["has_earth_soil_control"].fillna(False).mean()), 1),
                "reg_ctrl_pct": round(100.0 * float(grp["has_unamended_regolith_control"].fillna(False).mean()), 1),
                "stat_test_pct": round(100.0 * float(grp["has_statistical_test"].fillna(False).mean()), 1),
            }
        )
    division_rows.sort(key=lambda r: -r["n_pdfs"])

    # Top crops table with NCBITaxon and guild
    top_crops_table: list[dict[str, Any]] = []
    for crop, grp in pdfs.groupby("crop_common_name"):
        if str(crop) == "unspecified":
            continue
        sci = grp["crop_scientific_name"].dropna()
        tax = grp["crop_ncbitaxon"].dropna()
        gld = grp["crop_guild"].dropna()
        top_crops_table.append(
            {
                "crop": str(crop),
                "scientific": str(sci.iloc[0]) if len(sci) else "—",
                "ncbitaxon": str(tax.iloc[0]) if len(tax) else "—",
                "guild": str(gld.iloc[0]).replace("_", " ") if len(gld) else "—",
                "count": int(len(grp)),
                "pct": round(100.0 * len(grp) / n_pdfs, 1),
            }
        )
    top_crops_table.sort(key=lambda r: -r["count"])

    # Simulant breakdown
    simulant_rows: list[dict[str, Any]] = []
    for sim, cnt in pdfs["regolith_simulant"].value_counts().items():
        simulant_rows.append(
            {
                "simulant": str(sim).replace("_", " "),
                "count": int(cnt),
                "pct": round(100.0 * int(cnt) / n_pdfs, 1),
            }
        )

    # Amendment outcome breakdown
    amend_rows: list[dict[str, Any]] = []
    scored_trt = trt[trt["outcome_vs_regolith_control"].isin(["improved", "neutral", "reduced"])]
    for cat, grp in scored_trt.groupby("amendment_category"):
        n_tot = len(grp)
        n_imp = int((grp["outcome_vs_regolith_control"] == "improved").sum())
        n_red = int((grp["outcome_vs_regolith_control"] == "reduced").sum())
        p, lo, hi = wilson_ci(n_imp, n_tot)
        amend_rows.append(
            {
                "category": str(cat).replace("_", " "),
                "n_arms": int(n_tot),
                "n_improved": n_imp,
                "n_reduced": n_red,
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
        {"bottleneck": k.replace("_", " "), "count": v, "pct": round(100.0 * v / n_pdfs, 1)}
        for k, v in sorted(bn_counts.items(), key=lambda x: -x[1])[:9]
    ]

    # Exemplar studies from Spring 2026 Main Best in Show
    sp26 = pdfs[(pdfs["season_slug"] == "spring26") & (pdfs["track"] == "main")].sort_values("team_name")
    exemplars: list[dict[str, Any]] = []
    for _, r in sp26.iterrows():
        exemplars.append(
            {
                "team": str(r["team_name"]),
                "division": str(r["division_norm"]),
                "category": str(r["award_category"] or "Best in Show"),
                "target": str(r["celestial_body"]),
                "crop": str(r["crop_common_name"]),
                "title": str(r["project_title"] or "")[:115],
                "sha256_prefix": str(r["sha256"] or "")[:10],
            }
        )

    data = {
        "total_award_entries": int(len(reports)),
        "total_pdf_reports": int(len(pdfs)),
        "total_pages": int(pdfs["page_count"].fillna(0).sum()),
        "total_tables": int(pdfs["table_count"].fillna(0).sum()),
        "total_chars": int(pdfs["total_chars"].fillna(0).sum()),
        "digital_text_pdfs": int((pdfs["parse_quality"] == "digital_text").sum()),
        "scanned_pdfs": int((pdfs["parse_quality"] != "digital_text").sum()),
        "total_arms": int(len(arms)),
        "total_treatment_arms": int(len(trt)),
        "scored_treatment_arms": int(len(scored_trt)),
        "n_states": int(reports["location_state"].dropna().nunique()),
        "ncbitaxon_mapped": int(pdfs["crop_ncbitaxon"].notna().sum()),
        "ncbitaxon_pct": round(100.0 * float(pdfs["crop_ncbitaxon"].notna().mean()), 1),
        "earth_ctrl_pct": round(100.0 * float(pdfs["has_earth_soil_control"].fillna(False).mean()), 1),
        "reg_ctrl_pct": round(100.0 * float(pdfs["has_unamended_regolith_control"].fillna(False).mean()), 1),
        "stat_test_pct": round(100.0 * float(pdfs["has_statistical_test"].fillna(False).mean()), 1),
        "celestial_counts": {str(k): int(v) for k, v in pdfs["celestial_body"].value_counts().items()},
        "season_breakdown": season_rows,
        "division_rigor": division_rows,
        "top_crops": top_crops_table[:10],
        "simulant_breakdown": simulant_rows,
        "amendment_outcomes": amend_rows[:12],
        "top_bottlenecks": top_bottlenecks,
        "exemplar_studies": exemplars,
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
    bib_src = repo_root / "manuscript/references.bib"
    if bib_src.exists():
        shutil.copy2(bib_src, out_static.parent / "references.bib")
    return out_static
