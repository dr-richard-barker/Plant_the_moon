# Synthesis Manuscript (Interactive PDF Viewer)

Read the compiled **CoSE Meta-Analysis Synthesis Manuscript** directly below using the interactive PDF.js viewer, or download the publication PDF for offline reading.

<div id="cose-pdf-viewer" class="cose-pdf-shell" data-pdf-url="_static/manuscript/Plant_the_Moon_Meta_Analysis.pdf">
  <div class="cose-pdf-toolbar" role="toolbar" aria-label="Manuscript PDF controls">
    <button type="button" id="pdf-prev" aria-label="Previous page">← Prev</button>
    <label for="pdf-page-num" class="cose-sr-only">Page number</label>
    <input type="number" id="pdf-page-num" value="1" min="1" aria-label="Jump to page">
    <span id="pdf-page-count">/ —</span>
    <button type="button" id="pdf-next" aria-label="Next page">Next →</button>
    <span style="flex:1"></span>
    <button type="button" id="pdf-zoom-out" aria-label="Zoom out">−</button>
    <span id="pdf-zoom-label">125%</span>
    <button type="button" id="pdf-zoom-in" aria-label="Zoom in">+</button>
    <button type="button" id="pdf-fit">Fit Width</button>
    <button type="button" id="pdf-fullscreen">Fullscreen</button>
    <a class="cose-tool-btn" href="_static/manuscript/Plant_the_Moon_Meta_Analysis.pdf" download>Download PDF ↓</a>
    <a class="cose-tool-btn" href="_static/manuscript/references.bib" download>BibTeX (.bib) ↓</a>
  </div>
  <div id="pdf-status" class="cose-sr-only" role="status">Loading manuscript PDF...</div>
  <div id="pdf-stage" class="cose-pdf-stage">
    <p>Loading manuscript PDF…</p>
  </div>
</div>

## Manuscript Overview & Sections
1. **Structured Abstract & KPI Summary**: Background, FAIR pipeline architecture, empirical results across `324` award entries (`187` PDFs, `2,710` pages, `1,206` tables, `581` trial arms), and BLSS recommendations.
2. **1. Introduction**: Bioregenerative life support systems (BLSS), authentic Apollo lunar regolith transcriptomics (*Paul et al.*, 2022), lunar/Martian simulant standards (`LHS-1`, `LMS-1`, `MGS-1`), and citizen-science scaling.
3. **2. Materials & Methods**: Deterministic scraping & SHA-256 provenance, `PyMuPDF`/`pdfplumber` table extraction, Pydantic v2 hybrid extraction with verbatim quote verification, OBO Foundry ontology crosswalks (`NCBITaxon`, `ENVO`, `AGRO`, `CHEBI`, `PECO`) packaged in RO-Crate 1.1, and leak-free `StratifiedGroupKFold` ML modeling grouped by `report_id`.
4. **3. Results**: 7 data-driven tables and 4 multi-panel figures covering 12-season coverage, division-level experimental rigor, taxonomic/simulant distributions, UMAP protocol clustering, amendment efficacy with 95% Wilson CIs, grouped ML benchmarks with SHAP attributions, regolith bottlenecks, sparsity matrices, and `Spring 2026` exemplar innovations.
5. **4. Discussion & 5. Data Availability**: Coupled biogeochemical/hydraulic synergy in regolith remediation, closing the citizen-science control-group gap, and verified Nature-style references (`references.bib`).

<script src="_static/pdf-viewer.js"></script>
