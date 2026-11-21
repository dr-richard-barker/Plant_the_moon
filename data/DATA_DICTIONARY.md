# FAIR Data Dictionary

This project publishes two primary tabular tables (`reports` and `trial_arms`) plus an integrated explorer bundle (`cose_ptm_explorer.json`), all conforming to the JSON Schemas in `schemas/`.

## 1. `data/processed/reports.{csv,parquet,json}` (One Row per Award Entry)

| Column | Type | Units / Allowed Values | Missingness Semantics | Description |
| --- | --- | --- | --- | --- |
| `report_id` | string | unique slug + SHA1 suffix | Never null | Deterministic primary key linking manifest, extracted JSON, and trial arms. |
| `season` | string | e.g., `Spring 2026` | Never null | Competition season name. |
| `season_order` | integer | `1` (Spring 2021) – `12` (Spring 2026) | Never null | Chronological season sort index. |
| `track` | enum | `main`, `junior` | Never null | Main (`/` High School & Professional) vs Junior (`/jr/` Elementary & Middle). |
| `division_norm` | string | Standardized division label | Never null | Normalized student division level. |
| `award_tier` | string | `Best in Show`, `State Award`, etc. | Never null | Highest award tier parsed from page section. |
| `award_badges` | string | Semicolon-delimited badges | Empty if none | All merged award badges if a team won multiple awards in a season. |
| `has_pdf` | boolean | `true`, `false` | Never null | `false` for State Award cards lacking PDF report links. |
| `sha256` | string | 64-char hex digest | Null if `has_pdf=false` | SHA-256 hash of downloaded PDF for exact byte verification. |
| `parse_quality` | enum | `digital_text`, `sparse_text`, `image_or_scanned` | Null if no PDF | Diagnostic PDF text-layer density classification. |
| `extraction_method` | enum | `gemini_structured`, `heuristic` | Null if no PDF | Extraction backend provenance. |
| `celestial_body` | enum | `lunar`, `martian`, `both`, `unspecified` | Never null for PDFs | Target regolith environment. |
| `regolith_simulant` | enum | `LHS-1`, `LMS-1`, `MGS-1`, `JSC-1A`, etc. | Never null for PDFs | Standardized regolith simulant identifier. |
| `crop_common_name` | string | e.g., `radish`, `lettuce`, `spinach` | `unspecified` if unstated | Primary focal crop common name. |
| `crop_ncbitaxon` | string | e.g., `NCBITaxon:3726` | Null if unmapped | Linked NCBI Taxonomy identifier for semantic FAIR interoperability. |
| `crop_guild` | enum | `leafy_green`, `root`, `legume`, `fruiting`, `grain`, `herb`, `fungi`, `microgreen`, `mixed`, `other`, `unspecified` | Never null for PDFs | Botanical/functional crop guild. |
| `experimental_duration_days` | float | days | Null if unreported | Reported experiment duration in days. |
| `has_earth_soil_control` | boolean | `true`, `false` | Null if no PDF | Whether an Earth/potting soil positive control arm was reported. |
| `has_unamended_regolith_control` | boolean | `true`, `false` | Null if no PDF | Whether a 100% unamended regolith negative control was reported. |
| `quote_match_rate` | float | `0.0` – `1.0` | Null if no quotes | Fraction of arm evidence quotes verified in extracted PDF text. |

## 2. `data/processed/trial_arms.{csv,parquet,json}` (One Row per Experimental Arm)

| Column | Type | Units / Allowed Values | Description |
| --- | --- | --- | --- |
| `report_id` | string | Foreign key -> `reports.report_id` | Grouping key (used for `GroupKFold` to prevent leakage). |
| `arm_id` | string | e.g., `arm_1`, `arm_ctrl_regolith` | Arm identifier within report. |
| `is_control` | boolean | `true`, `false` | Whether arm represents a baseline control. |
| `control_type` | enum | `earth_soil`, `unamended_regolith`, `none` | Control arm role. |
| `regolith_pct` | float | `0` – `100` (%) | Percentage of regolith simulant in growth substrate. |
| `amendment_category` | enum | Controlled vocabulary (14 classes) | Standardized intervention or substrate amendment category. |
| `amendment_ontology_uri` | URI | ENVO / AGRO / CHEBI / PECO OBO URI | Linked ontology concept URI (crosswalked in `ontology_mappings.json`). |
| `germination_rate_pct` | float | `0` – `100` (%) | Reported seed germination percentage. |
| `mean_shoot_height_cm` | float | cm | Mean shoot/plant height at harvest or final measurement. |
| `mean_fresh_biomass_g` | float | g | Mean fresh shoot or whole-plant mass. |
| `substrate_ph` | float | `0` – `14` | Measured substrate pH. |
| `outcome_vs_regolith_control` | enum | `improved`, `neutral`, `reduced`, `not_reported` | Direction of plant performance relative to unamended regolith control. |
| `delta_germination_pp` | float | percentage points | Treatment minus unamended regolith control germination rate. |
| `log_response_ratio_height` | float | $\ln(\bar{X}_{\text{trt}} / \bar{X}_{\text{ctrl}})$ | Natural log response ratio for shoot height vs regolith control. |
| `log_response_ratio_biomass` | float | $\ln(\bar{X}_{\text{trt}} / \bar{X}_{\text{ctrl}})$ | Natural log response ratio for biomass vs regolith control. |
| `missing_germination` / `missing_height` / `missing_biomass` | boolean | `true`, `false` | Explicit missingness indicator flags. |
| `evidence_quote` | string | Verbatim excerpt | Direct provenance quote supporting extracted parameters. |
| `page_number` | integer | 1-based page index | Source PDF page where `evidence_quote` appears. |
