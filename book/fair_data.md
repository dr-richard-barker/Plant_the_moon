# FAIR Data, Schemas & Downloads

All derived datasets, JSON Schemas, ontology crosswalks, and manuscript artifacts follow the **FAIR** principles:

## Direct Downloads
- [Synthesized Manuscript PDF (`Plant_the_Moon_Meta_Analysis.pdf`)](_static/manuscript/Plant_the_Moon_Meta_Analysis.pdf)
- [Normalized Reports Table (`reports.csv`)](_static/data/reports.csv)
- [Normalized Trial Arms Table (`trial_arms.csv`)](_static/data/trial_arms.csv)
- [Explorer JSON Bundle (`cose_ptm_explorer.json`)](_static/data/cose_ptm_explorer.json)
- [OBO Ontology Crosswalks (`ontology_mappings.json`)](_static/data/ontology_mappings.json)

## Repository FAIR Standards
- **Findable**: `CITATION.cff`, `codemeta.json`, and `ro-crate-metadata.json` with persistent ORCID (`0000-0001-5681-9857`) and repository identifiers.
- **Accessible**: Open MIT / CC-BY-4.0 GitHub repository + static GitHub Pages mirror with zero paywalls or login walls.
- **Interoperable**: Draft 2020-12 JSON Schemas (`schemas/report_manifest.schema.json`, `schemas/experiment_record.schema.json`) + `NCBITaxon`, `ENVO`, `AGRO`, `CHEBI`, and `PECO` URIs.
- **Reusable**: Locked `uv` environment (`pyproject.toml` + `uv.lock`), SHA-256 manifests (`data/raw/manifest.csv`), automated `pytest` suite, and `data/DATA_DICTIONARY.md`.
