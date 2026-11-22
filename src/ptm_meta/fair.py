"""FAIR packaging: RO-Crate 1.1 generation and JSON Schema validation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_ro_crate(repo_root: Path) -> Path:
    """Generate ro-crate-metadata.json (RO-Crate 1.1) cataloging all code, schemas, and data."""
    candidate_files = [
        ("CITATION.cff", "TextFile", "Citation metadata (CFF 1.2.0)"),
        ("codemeta.json", "SoftwareSourceCode", "CodeMeta v3.0 metadata"),
        ("README.md", "TextFile", "Project documentation"),
        ("data/DATA_DICTIONARY.md", "TextFile", "FAIR data dictionary"),
        ("schemas/report_manifest.schema.json", "File", "JSON Schema for scraped PDF manifest"),
        ("schemas/experiment_record.schema.json", "File", "JSON Schema for structured extractions"),
        ("data/raw/manifest.csv", "Dataset", "Scraped awards metadata & SHA-256 PDF provenance manifest (CSV)"),
        ("data/raw/manifest.json", "Dataset", "Scraped awards metadata & SHA-256 PDF provenance manifest (JSON)"),
        ("data/processed/reports.csv", "Dataset", "Normalized report-level metadata & quality dataset (CSV)"),
        ("data/processed/reports.parquet", "Dataset", "Normalized report-level metadata & quality dataset (Parquet)"),
        ("data/processed/trial_arms.csv", "Dataset", "Normalized experimental trial-arm meta-analysis table (CSV)"),
        ("data/processed/trial_arms.parquet", "Dataset", "Normalized experimental trial-arm meta-analysis table (Parquet)"),
        ("data/processed/cose_ptm_explorer.json", "Dataset", "Interactive CoSE GitPage explorer JSON bundle"),
        ("data/processed/ontology_mappings.json", "Dataset", "FAIR ontology crosswalks (NCBITaxon, ENVO, AGRO, Exolith)"),
        ("manuscript/ptm_manuscript.typ", "TextFile", "Typst source for CoSE synthesis manuscript"),
        ("manuscript/ptm_presentation.typ", "TextFile", "Typst 16:9 source for multi-stakeholder presentation deck"),
        ("manuscript/references.bib", "TextFile", "Verified BibTeX bibliography for CoSE synthesis manuscript"),
        ("book/_static/manuscript/Plant_the_Moon_Meta_Analysis.pdf", "File", "Compiled CoSE synthesis manuscript PDF"),
        ("book/_static/manuscript/Plant_the_Moon_Stakeholder_Presentation.pdf", "File", "Compiled 16:9 multi-stakeholder presentation PDF"),
        ("book/notebooks/01_corpus_eda.ipynb", "File", "Corpus provenance & scientometric EDA notebook"),
        ("book/notebooks/02_unsupervised_clustering.ipynb", "File", "Unsupervised NLP & experimental archetype clustering notebook"),
        ("book/notebooks/03_meta_analysis_ml.ipynb", "File", "Quantitative meta-analysis & predictive ML comparison notebook"),
        ("book/notebooks/04_ai_synthesis_gaps.ipynb", "File", "Failure modes, research gaps & synthesis notebook"),
    ]

    has_part: list[dict[str, str]] = []
    entities: list[dict[str, Any]] = []

    for rel, rdf_type, desc in candidate_files:
        fp = repo_root / rel
        if not fp.exists():
            continue
        has_part.append({"@id": rel})
        entities.append(
            {
                "@id": rel,
                "@type": rdf_type,
                "name": fp.name,
                "description": desc,
                "contentSize": fp.stat().st_size,
                "sha256": _sha256_file(fp),
            }
        )

    crate = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {
                "@type": "CreativeWork",
                "@id": "ro-crate-metadata.json",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
                "about": {"@id": "./"},
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "Plant the Moon Challenge FAIR Meta-Analysis (Spring 2021 – Spring 2026)",
                "description": (
                    "Reproducible scraping, SHA-256 provenance manifest, structured extraction, "
                    "and AI/ML meta-analysis of student regolith plant-growth reports from plantthemoon.com."
                ),
                "datePublished": datetime.now(timezone.utc).date().isoformat(),
                "license": {"@id": "https://spdx.org/licenses/MIT"},
                "author": {"@id": "https://orcid.org/0000-0001-5681-9857"},
                "hasPart": has_part,
            },
            {
                "@id": "https://orcid.org/0000-0001-5681-9857",
                "@type": "Person",
                "name": "Richard J. Barker",
                "affiliation": {"@id": "https://cosecloud.com"},
            },
            {
                "@id": "https://cosecloud.com",
                "@type": "Organization",
                "name": "Collaborative Science Environment (CoSE)",
            },
            *entities,
        ],
    }

    out_path = repo_root / "ro-crate-metadata.json"
    out_path.write_text(json.dumps(crate, indent=2), encoding="utf-8")
    return out_path


def validate_fair_artifacts(repo_root: Path) -> dict[str, Any]:
    """Validate schemas, manifest, extracted JSONs, and RO-Crate integrity."""
    report: dict[str, Any] = {
        "manifest_checked": False,
        "manifest_count": 0,
        "extractions_checked": 0,
        "ro_crate_valid": False,
        "errors": [],
    }

    manifest_schema_path = repo_root / "schemas/report_manifest.schema.json"
    exp_schema_path = repo_root / "schemas/experiment_record.schema.json"
    manifest_json_path = repo_root / "data/raw/manifest.json"

    if manifest_schema_path.exists() and manifest_json_path.exists():
        schema = json.loads(manifest_schema_path.read_text(encoding="utf-8"))
        data = json.loads(manifest_json_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=schema)
        report["manifest_checked"] = True
        report["manifest_count"] = len(data)

    ext_dir = repo_root / "data/interim/llm_extractions"
    if exp_schema_path.exists() and ext_dir.exists():
        exp_schema = json.loads(exp_schema_path.read_text(encoding="utf-8"))
        for fp in sorted(ext_dir.glob("*.json")):
            bundle = json.loads(fp.read_text(encoding="utf-8"))
            jsonschema.validate(instance=bundle["extraction"], schema=exp_schema)
            report["extractions_checked"] += 1

    crate_path = repo_root / "ro-crate-metadata.json"
    if crate_path.exists():
        crate = json.loads(crate_path.read_text(encoding="utf-8"))
        graph = crate.get("@graph", [])
        if any(n.get("@id") == "./" for n in graph) and any(
            n.get("@id") == "ro-crate-metadata.json" for n in graph
        ):
            report["ro_crate_valid"] = True
        else:
            report["errors"].append("ro-crate-metadata.json missing required root entities")

    if report["errors"]:
        raise ValueError("; ".join(report["errors"]))
    return report
