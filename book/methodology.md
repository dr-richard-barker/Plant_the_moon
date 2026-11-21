# FAIR Methodology & Provenance

## Pipeline Architecture
1. **Archive Scraping (`ptm_meta.scrape`)**: Crawls all 24 WordPress/Elementor pages listed in `configs/seasons.yaml`, preserves raw HTML snapshots, parses Best in Show, State Award, and NASA Space Grant cards, repairs UTF-8 mojibake, and merges overlapping award badges deterministically.
2. **SHA-256 PDF Acquisition (`ptm_meta.fetch`)**: Downloads all `187` unique PDF reports with retry/backoff, computes SHA-256 checksums and byte sizes, and verifies `page_count` via `PyMuPDF`.
3. **PDF Text & Table Parsing (`ptm_meta.pdf_parse`)**: Extracts per-page text (`3.43M` characters across `2,710` pages) and structured tables (`1,206` tables via `pdfplumber`), classifying each file (`digital_text` vs. `image_or_scanned`).
4. **Hybrid Structured Extraction (`ptm_meta.extract`)**: Enforces `schemas/experiment_record.schema.json` via Pydantic v2, supporting both **Gemini Structured Multimodal Extraction** (`--backend gemini`) and a deterministic **table-aware offline heuristic baseline** (`--backend heuristic`), always recording `extraction_method` and verbatim `evidence_quote` + `page_number`.
5. **Ontology Crosswalk & Normalization (`ptm_meta.ontologies`, `normalize.py`)**: Maps crop species to `NCBITaxon`, amendments to `ENVO`/`AGRO`/`CHEBI`/`PECO`, and simulants to Exolith/NASA standards, exporting CSV, Parquet, JSON, and RO-Crate 1.1 (`ro-crate-metadata.json`).

## Limitations & Transparency
- Under offline heuristic extraction, dense narrative prose and heterogeneous student tables yield lower numerical recall than LLM multimodal extraction; all `missing_*` indicators and `extraction_method` provenance fields are preserved explicitly so analyses never conflate missing measurements with zero growth.
- Original student PDFs remain the intellectual property of the student teams and the Institute of Competition Sciences (`plantthemoon.com`).
