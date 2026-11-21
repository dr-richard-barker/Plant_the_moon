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
  </div>
  <div id="pdf-status" class="cose-sr-only" role="status">Loading manuscript PDF...</div>
  <div id="pdf-stage" class="cose-pdf-stage">
    <p>Loading manuscript PDF…</p>
  </div>
</div>

<script src="_static/pdf-viewer.js"></script>
