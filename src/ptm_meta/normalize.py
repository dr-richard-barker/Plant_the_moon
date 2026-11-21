"""Normalization, effect-size computation, and FAIR analytical dataset export."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd

from ptm_meta.models import ManifestRecord, ReportExtraction
from ptm_meta.ontologies import (
    AMENDMENT_ONTOLOGY,
    CROP_ONTOLOGY,
    export_ontology_mappings,
)


def normalize_division(raw: str | None, track: str) -> str:
    txt = (raw or "").lower()
    if "elementary" in txt:
        return "Elementary School"
    if "middle" in txt:
        return "Middle School"
    if "high" in txt:
        return "High School"
    if any(k in txt for k in ("professional", "undergrad", "university", "college")):
        return "Professional / University"
    return "Elementary / Middle (Jr)" if track == "junior" else "High School / Professional"


def _safe_lrr(trt: float | None, ctrl: float | None) -> float | None:
    if trt is None or ctrl is None or trt <= 0 or ctrl <= 0:
        return None
    return round(math.log(trt / ctrl), 4)


def _safe_pct_change(trt: float | None, ctrl: float | None) -> float | None:
    if trt is None or ctrl is None or ctrl == 0:
        return None
    return round(((trt - ctrl) / ctrl) * 100.0, 2)


def normalize_and_export(
    manifest_json: Path,
    parsed_dir: Path,
    extractions_dir: Path,
    processed_dir: Path,
    static_data_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build normalized reports & trial_arms FAIR tables + explorer JSON bundle."""
    manifest_items = [
        ManifestRecord.model_validate(item)
        for item in json.loads(manifest_json.read_text(encoding="utf-8"))
    ]

    report_rows: list[dict[str, Any]] = []
    arm_rows: list[dict[str, Any]] = []
    explorer_records: list[dict[str, Any]] = []

    for rec in manifest_items:
        parsed_path = parsed_dir / f"{rec.report_id}.json"
        ext_path = extractions_dir / f"{rec.report_id}.json"
        parsed = json.loads(parsed_path.read_text(encoding="utf-8")) if parsed_path.exists() else {}
        ext_bundle = json.loads(ext_path.read_text(encoding="utf-8")) if ext_path.exists() else {}

        ext: ReportExtraction | None = None
        if ext_bundle.get("extraction"):
            ext = ReportExtraction.model_validate(ext_bundle["extraction"])
        prov = ext_bundle.get("provenance_audit", {})

        division_norm = normalize_division(rec.division, rec.track)

        # Find unamended regolith control baselines within this report for paired effect metrics
        ctrl_germ: float | None = None
        ctrl_height: float | None = None
        ctrl_biomass: float | None = None
        if ext:
            reg_ctrls = [a for a in ext.arms if a.control_type == "unamended_regolith"]
            if reg_ctrls:
                c = reg_ctrls[0]
                ctrl_germ = c.germination_rate_pct
                ctrl_height = c.mean_shoot_height_cm
                ctrl_biomass = c.mean_fresh_biomass_g or c.mean_dry_biomass_g

        n_arms = len(ext.arms) if ext else 0
        n_improved = (
            sum(1 for a in ext.arms if not a.is_control and a.outcome_vs_regolith_control == "improved")
            if ext
            else 0
        )
        amendments_list = (
            sorted({a.amendment_category for a in ext.arms if not a.is_control})
            if ext
            else []
        )

        crop_ont = CROP_ONTOLOGY.get(ext.crop_common_name, {}) if ext else {}
        report_row = {
            "report_id": rec.report_id,
            "season": rec.season,
            "season_slug": rec.season_slug,
            "season_order": rec.season_order,
            "year": rec.year,
            "term": rec.term,
            "track": rec.track,
            "division_raw": rec.division,
            "division_norm": division_norm,
            "award_tier": rec.award_tier,
            "award_category": rec.award_category,
            "award_badges": "; ".join(rec.award_badges),
            "team_name": rec.team_name,
            "project_title": rec.project_title,
            "location_city": rec.location_city,
            "location_state": rec.location_state,
            "has_pdf": rec.has_pdf,
            "pdf_url": rec.pdf_url,
            "source_page_url": rec.source_page_url,
            "sha256": rec.sha256,
            "byte_size": rec.byte_size,
            "page_count": parsed.get("page_count") or rec.page_count,
            "total_chars": parsed.get("total_chars"),
            "avg_chars_per_page": parsed.get("avg_chars_per_page"),
            "table_count": parsed.get("table_count"),
            "parse_quality": parsed.get("parse_quality"),
            "extraction_method": ext.extraction_method if ext else None,
            "model_name": ext.model_name if ext else None,
            "celestial_body": ext.celestial_body if ext else None,
            "regolith_simulant": ext.regolith_simulant if ext else None,
            "crop_common_name": ext.crop_common_name if ext else None,
            "crop_scientific_name": (ext.crop_scientific_name or crop_ont.get("scientific_name")) if ext else None,
            "crop_ncbitaxon": crop_ont.get("ncbitaxon"),
            "crop_guild": ext.crop_guild if ext else None,
            "experimental_duration_days": ext.experimental_duration_days if ext else None,
            "total_plants_or_pots": ext.total_plants_or_pots if ext else None,
            "replicates_per_treatment": ext.replicates_per_treatment if ext else None,
            "has_earth_soil_control": ext.has_earth_soil_control if ext else None,
            "has_unamended_regolith_control": ext.has_unamended_regolith_control if ext else None,
            "statistical_tests_reported": "; ".join(ext.statistical_tests_reported) if ext else "",
            "has_statistical_test": bool(ext and ext.statistical_tests_reported),
            "data_availability": ext.data_availability if ext else None,
            "primary_bottlenecks": "; ".join(ext.primary_bottlenecks) if ext else "",
            "amendment_categories": "; ".join(amendments_list),
            "n_arms": n_arms,
            "n_improved_arms": n_improved,
            "quote_match_rate": prov.get("quote_match_rate"),
            "key_hypothesis": ext.key_hypothesis if ext else None,
            "summary_findings": ext.summary_findings if ext else None,
        }
        report_rows.append(report_row)

        arm_dicts_for_explorer: list[dict[str, Any]] = []
        if ext:
            for arm in ext.arms:
                biomass = arm.mean_fresh_biomass_g or arm.mean_dry_biomass_g
                delta_germ = (
                    round(arm.germination_rate_pct - ctrl_germ, 2)
                    if (arm.germination_rate_pct is not None and ctrl_germ is not None and not arm.is_control)
                    else None
                )
                arm_dict = {
                    "report_id": rec.report_id,
                    "season": rec.season,
                    "season_order": rec.season_order,
                    "year": rec.year,
                    "track": rec.track,
                    "division_norm": division_norm,
                    "team_name": rec.team_name,
                    "celestial_body": ext.celestial_body,
                    "regolith_simulant": ext.regolith_simulant,
                    "crop_common_name": ext.crop_common_name,
                    "crop_guild": ext.crop_guild,
                    "experimental_duration_days": ext.experimental_duration_days,
                    "has_earth_soil_control": ext.has_earth_soil_control,
                    "has_unamended_regolith_control": ext.has_unamended_regolith_control,
                    "has_statistical_test": bool(ext.statistical_tests_reported),
                    "arm_id": arm.arm_id,
                    "arm_label": arm.arm_label,
                    "is_control": arm.is_control,
                    "control_type": arm.control_type,
                    "regolith_pct": arm.regolith_pct,
                    "amendment_category": arm.amendment_category,
                    "amendment_ontology_uri": AMENDMENT_ONTOLOGY.get(arm.amendment_category, {}).get("uri"),
                    "amendment_detail": arm.amendment_detail,
                    "amendment_dose": arm.amendment_dose,
                    "germination_rate_pct": arm.germination_rate_pct,
                    "survival_rate_pct": arm.survival_rate_pct,
                    "mean_shoot_height_cm": arm.mean_shoot_height_cm,
                    "mean_root_length_cm": arm.mean_root_length_cm,
                    "mean_fresh_biomass_g": arm.mean_fresh_biomass_g,
                    "mean_dry_biomass_g": arm.mean_dry_biomass_g,
                    "substrate_ph": arm.substrate_ph,
                    "outcome_vs_regolith_control": arm.outcome_vs_regolith_control,
                    "reported_effect_pct": arm.reported_effect_pct,
                    "ctrl_germination_pct": ctrl_germ,
                    "delta_germination_pp": delta_germ,
                    "pct_change_height": _safe_pct_change(arm.mean_shoot_height_cm, ctrl_height) if not arm.is_control else None,
                    "log_response_ratio_height": _safe_lrr(arm.mean_shoot_height_cm, ctrl_height) if not arm.is_control else None,
                    "pct_change_biomass": _safe_pct_change(biomass, ctrl_biomass) if not arm.is_control else None,
                    "log_response_ratio_biomass": _safe_lrr(biomass, ctrl_biomass) if not arm.is_control else None,
                    "missing_germination": arm.germination_rate_pct is None,
                    "missing_height": arm.mean_shoot_height_cm is None,
                    "missing_biomass": biomass is None,
                    "evidence_quote": arm.evidence_quote,
                    "page_number": arm.page_number,
                }
                arm_rows.append(arm_dict)
                arm_dicts_for_explorer.append(
                    {
                        "arm_label": arm.arm_label,
                        "is_control": arm.is_control,
                        "amendment_category": arm.amendment_category,
                        "amendment_detail": arm.amendment_detail,
                        "germination_rate_pct": arm.germination_rate_pct,
                        "mean_shoot_height_cm": arm.mean_shoot_height_cm,
                        "mean_fresh_biomass_g": arm.mean_fresh_biomass_g,
                        "outcome_vs_regolith_control": arm.outcome_vs_regolith_control,
                        "evidence_quote": arm.evidence_quote,
                        "page_number": arm.page_number,
                    }
                )

        explorer_records.append(
            {
                **report_row,
                "arms": arm_dicts_for_explorer,
            }
        )

    processed_dir.mkdir(parents=True, exist_ok=True)
    df_reports = pd.DataFrame(report_rows)
    df_arms = pd.DataFrame(arm_rows)

    df_reports.to_csv(processed_dir / "reports.csv", index=False)
    df_reports.to_parquet(processed_dir / "reports.parquet", index=False)
    (processed_dir / "reports.json").write_text(
        json.dumps(report_rows, indent=2), encoding="utf-8"
    )

    df_arms.to_csv(processed_dir / "trial_arms.csv", index=False)
    df_arms.to_parquet(processed_dir / "trial_arms.parquet", index=False)
    (processed_dir / "trial_arms.json").write_text(
        json.dumps(arm_rows, indent=2), encoding="utf-8"
    )

    # Compact explorer JSON (sanitize NaN/Inf cleanly via pandas -> json)
    explorer_json = json.dumps(explorer_records, indent=2, default=str)
    explorer_json = re.sub(r"\bNaN\b", "null", explorer_json)
    (processed_dir / "cose_ptm_explorer.json").write_text(explorer_json, encoding="utf-8")
    export_ontology_mappings(processed_dir / "ontology_mappings.json")

    if static_data_dir is not None:
        static_data_dir.mkdir(parents=True, exist_ok=True)
        (static_data_dir / "cose_ptm_explorer.json").write_text(explorer_json, encoding="utf-8")
        export_ontology_mappings(static_data_dir / "ontology_mappings.json")
        df_reports.to_csv(static_data_dir / "reports.csv", index=False)
        df_arms.to_csv(static_data_dir / "trial_arms.csv", index=False)

    return df_reports, df_arms
