# Plant the Moon Challenge FAIR Meta-Analysis (CoSE)

A reproducible, FAIR-compliant (Findable, Accessible, Interoperable, Reusable) pipeline and **CoSE-styled Jupyter Book** analyzing student regolith plant-growth reports across the **Plant the Moon Challenge** archive (`Spring 2021`–`Spring 2026`, Main & Junior divisions).

## Key Features
- **Complete Archive Provenance**: Scrapes all 24 awards pages on `plantthemoon.com` (Main + `/jr/`), stores raw HTML snapshots, downloads PDFs with SHA-256 verification, and tracks canonical source URLs in `data/raw/manifest.{csv,json}`.
- **Hybrid AI/ML Extraction**: Extracts per-page text and tables (`PyMuPDF` + `pdfplumber`) followed by schema-enforced structured extraction (Gemini Structured Outputs with native multimodal PDF fallback for scanned posters/slide decks, plus a deterministic offline heuristic baseline) anchored to verbatim `evidence_quote` + `page_number` provenance.
- **Rigorous AI/ML Meta-Analysis**: Four executable Jupyter notebooks implementing corpus scientometrics, NLP + experimental clustering, effect-size meta-regression, and leak-free (`GroupKFold` by `report_id`) predictive modeling with SHAP interpretability.
- **CoSE-Styled GitHub Pages Portal**: Builds via Jupyter Book (`book/`) using the Collaborative Science Environment (CoSE) aesthetic (`#004053` / `#0f7f9f` / `#3f7d4e`, `IBM Plex Sans` & `IBM Plex Mono`, light/dark toggle) and an interactive client-side report explorer.
- **FAIR Standards**: Includes `CITATION.cff`, `codemeta.json`, JSON Schemas (`schemas/`), `ro-crate-metadata.json`, `data/DATA_DICTIONARY.md`, `pytest` suite, and GitHub Actions CI/Pages deployment.

## Quickstart (`uv`)

```bash
uv sync --extra dev
uv run pytest -v

# 1. Scrape archive pages & verify PDF downloads (requires network access)
uv run ptm-meta scrape
uv run ptm-meta fetch

# 2. Parse PDFs & run structured extraction
uv run ptm-meta parse
# Add GEMINI_API_KEY to ~/.env or .env for LLM extraction; otherwise heuristic baseline runs
uv run ptm-meta extract --backend auto

# 3. Normalize FAIR datasets, generate RO-Crate, and validate schemas
uv run ptm-meta normalize
uv run ptm-meta build-fair

# 4. Execute analysis notebooks & build CoSE Jupyter Book
uv run jupyter nbconvert --to notebook --execute --inplace book/notebooks/*.ipynb
uv run jupyter-book build book/
```

## License & Attribution
- Software & pipeline code: MIT License ([`LICENSE`](LICENSE)).
- Derived structured metadata & synthesis outputs: CC-BY-4.0 with full provenance links to original student teams and the Institute of Competition Sciences (`https://plantthemoon.com/`).
- Part of the **Collaborative Science Environment (CoSE)** open science ecosystem (`https://cosecloud.com/`).
