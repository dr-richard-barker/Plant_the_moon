"""Unit tests for heuristic extraction, quote verification, JSON Schemas, and RO-Crate."""

import json
from pathlib import Path

import jsonschema

from ptm_meta.extract import extract_heuristic, verify_quote_provenance
from ptm_meta.fair import build_ro_crate, validate_fair_artifacts
from ptm_meta.models import ManifestRecord


def test_heuristic_extraction_and_schema(tmp_path: Path) -> None:
    rec = ManifestRecord(
        report_id="spring26-main-team-shonik-abc123",
        season="Spring 2026",
        season_slug="spring26",
        season_order=12,
        year=2026,
        term="Spring",
        track="main",
        division="High School Level",
        award_tier="Best in Show",
        award_category="Experimental Design",
        award_badges=["Best in Show: Experimental Design"],
        team_name="Team Shonik",
        project_title="Microbial Necromass on Radish Growth in Lunar Regolith Simulant",
        pdf_url="https://plantthemoon.com/wp-content/uploads/2026/05/Shonik.pdf",
        source_page_url="https://plantthemoon.com/awards-spring26/",
        has_pdf=True,
    )
    parsed = {
        "report_id": rec.report_id,
        "page_count": 3,
        "total_chars": 1200,
        "avg_chars_per_page": 400.0,
        "table_count": 1,
        "parse_quality": "digital_text",
        "pages": [
            {
                "page_number": 1,
                "text": (
                    "We hypothesized that inactivated microbial necromass increases Raphanus sativus "
                    "germination in LHS-1 lunar regolith simulant over a 35-day trial. Controls included "
                    "potting soil and 100% unamended regolith."
                ),
                "tables": [],
            },
            {
                "page_number": 2,
                "text": (
                    "Radish germination reached 88% in the microbial necromass treatment, significantly "
                    "higher than the unamended LHS-1 control (ANOVA, p < 0.05). Alkaline pH (9.4) and "
                    "water retention remained primary bottlenecks."
                ),
                "tables": [],
            },
        ],
    }

    ext = extract_heuristic(rec, parsed)
    assert ext.celestial_body == "lunar"
    assert ext.regolith_simulant == "LHS-1"
    assert ext.crop_common_name == "radish"
    assert ext.experimental_duration_days == 35.0
    assert ext.has_earth_soil_control is True
    assert ext.has_unamended_regolith_control is True
    assert "ANOVA" in ext.statistical_tests_reported
    assert "alkaline_ph" in ext.primary_bottlenecks

    audit = verify_quote_provenance(ext, parsed)
    assert audit["quotes_checked"] >= 1
    assert audit["quote_match_rate"] == 1.0

    # Validate against repository JSON Schema
    repo_root = Path(__file__).resolve().parents[1]
    exp_schema = json.loads((repo_root / "schemas/experiment_record.schema.json").read_text())
    jsonschema.validate(instance=ext.model_dump(), schema=exp_schema)


def test_ro_crate_generation_and_validation(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    (tmp_path / "schemas").mkdir()
    (tmp_path / "data/raw").mkdir(parents=True)
    (tmp_path / "data/interim/llm_extractions").mkdir(parents=True)
    for fname in ("report_manifest.schema.json", "experiment_record.schema.json"):
        (tmp_path / "schemas" / fname).write_text((repo_root / "schemas" / fname).read_text())
    (tmp_path / "README.md").write_text("# Test\n")
    (tmp_path / "data/raw/manifest.json").write_text("[]")

    crate_path = build_ro_crate(tmp_path)
    assert crate_path.exists()
    rep = validate_fair_artifacts(tmp_path)
    assert rep["manifest_checked"] is True
    assert rep["ro_crate_valid"] is True
