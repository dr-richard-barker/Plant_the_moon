"""Unit tests for normalization math and leak-free grouped ML pipelines."""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ptm_meta.analysis import build_modeling_dataset, evaluate_grouped_models
from ptm_meta.models import ManifestRecord, ReportExtraction, TrialArm
from ptm_meta.normalize import normalize_and_export


def test_normalize_paired_effects(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    parsed_dir = tmp_path / "parsed"
    ext_dir = tmp_path / "ext"
    proc_dir = tmp_path / "proc"
    raw_dir.mkdir()
    parsed_dir.mkdir()
    ext_dir.mkdir()

    rec = ManifestRecord(
        report_id="spring26-main-test-111111",
        season="Spring 2026",
        season_slug="spring26",
        season_order=12,
        year=2026,
        term="Spring",
        track="main",
        division="High School Level",
        award_tier="Best in Show",
        team_name="Team Test",
        source_page_url="https://plantthemoon.com/awards-spring26/",
        has_pdf=True,
    )
    (raw_dir / "manifest.json").write_text(json.dumps([rec.model_dump()]))
    (parsed_dir / f"{rec.report_id}.json").write_text(
        json.dumps({"page_count": 4, "total_chars": 2000, "avg_chars_per_page": 500, "table_count": 1, "parse_quality": "digital_text"})
    )
    ext = ReportExtraction(
        report_id=rec.report_id,
        extraction_method="heuristic",
        celestial_body="lunar",
        regolith_simulant="LHS-1",
        crop_common_name="lettuce",
        crop_guild="leafy_green",
        has_earth_soil_control=False,
        has_unamended_regolith_control=True,
        summary_findings="Compost doubled lettuce shoot height.",
        arms=[
            TrialArm(
                arm_id="ctrl",
                is_control=True,
                control_type="unamended_regolith",
                amendment_category="none_control",
                germination_rate_pct=40.0,
                mean_shoot_height_cm=5.0,
                mean_fresh_biomass_g=1.0,
                outcome_vs_regolith_control="neutral",
            ),
            TrialArm(
                arm_id="trt",
                is_control=False,
                control_type="none",
                amendment_category="organic_compost_manure",
                germination_rate_pct=80.0,
                mean_shoot_height_cm=10.0,
                mean_fresh_biomass_g=2.5,
                outcome_vs_regolith_control="improved",
            ),
        ],
    )
    (ext_dir / f"{rec.report_id}.json").write_text(
        json.dumps({"extraction": ext.model_dump(), "provenance_audit": {"quote_match_rate": 1.0}})
    )

    df_r, df_a = normalize_and_export(raw_dir / "manifest.json", parsed_dir, ext_dir, proc_dir)
    assert len(df_r) == 1
    assert len(df_a) == 2

    trt = df_a[df_a["arm_id"] == "trt"].iloc[0]
    assert trt["delta_germination_pp"] == 40.0
    assert trt["pct_change_height"] == 100.0
    assert math.isclose(trt["log_response_ratio_height"], math.log(2.0), rel_tol=1e-3)
    assert math.isclose(trt["log_response_ratio_biomass"], math.log(2.5), rel_tol=1e-3)


def test_grouped_split_prevents_report_leakage() -> None:
    df = pd.DataFrame(
        {
            "report_id": ["r1", "r1", "r2", "r2", "r3", "r3", "r4", "r4", "r5", "r5"],
            "celestial_body": ["lunar", "lunar", "martian", "martian", "lunar", "lunar", "martian", "martian", "lunar", "lunar"],
            "regolith_pct": [100.0, 75.0, 100.0, 50.0, np.nan, 80.0, 100.0, 70.0, 90.0, 60.0],
            "target": [0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
        }
    )
    gss = GroupShuffleSplit(n_splits=1, test_size=0.4, random_state=42)
    train_idx, test_idx = next(gss.split(df, df["target"], groups=df["report_id"]))
    train_reports = set(df.iloc[train_idx]["report_id"])
    test_reports = set(df.iloc[test_idx]["report_id"])
    assert train_reports.isdisjoint(test_reports)

    pre = ColumnTransformer(
        [
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), ["regolith_pct"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["celestial_body"]),
        ]
    )
    pipe = Pipeline([("pre", pre), ("clf", LogisticRegression())])
    pipe.fit(df.iloc[train_idx][["regolith_pct", "celestial_body"]], df.iloc[train_idx]["target"])
    preds = pipe.predict(df.iloc[test_idx][["regolith_pct", "celestial_body"]])
    assert len(preds) == len(test_idx)


def test_analysis_build_and_evaluate(tmp_path: Path) -> None:
    reports = pd.DataFrame(
        [
            {
                "report_id": f"r{i}",
                "season_order": 12,
                "year": 2026,
                "track": "main",
                "division_norm": "High School",
                "experimental_duration_days": 30.0 if i % 2 == 0 else np.nan,
                "has_earth_soil_control": True,
                "has_unamended_regolith_control": True,
                "has_statistical_test": i % 3 == 0,
                "table_count": 2,
                "page_count": 8,
            }
            for i in range(15)
        ]
    )
    arms = pd.DataFrame(
        [
            {
                "report_id": f"r{i}",
                "is_control": False,
                "outcome_vs_regolith_control": "improved" if (i + j) % 2 == 0 else "reduced",
                "regolith_pct": 85.0,
                "celestial_body": "lunar" if i % 2 == 0 else "martian",
                "regolith_simulant": "LHS-1" if i % 2 == 0 else "MGS-1",
                "crop_guild": "root",
                "amendment_category": "organic_compost_manure" if j == 0 else "biochar_carbon",
            }
            for i in range(15)
            for j in range(2)
        ]
    )
    df_ml = build_modeling_dataset(arms, reports)
    assert len(df_ml) == 30
    assert "missing_duration" in df_ml.columns

    metrics_path = tmp_path / "ml_metrics.json"
    res = evaluate_grouped_models(df_ml, out_json=metrics_path, seed=42)
    assert metrics_path.exists()
    assert res["n_unique_reports"] == 15
    assert len(res["models"]) == 4

