/* Interactive PDF.js Manuscript Viewer with native <object> fallback */
(function () {
  "use strict";

  var container = document.getElementById("cose-pdf-viewer");
  if (!container) return;

  var pdfUrl = container.dataset.pdfUrl;
  var stage = document.getElementById("pdf-stage");
  var pageInput = document.getElementById("pdf-page-num");
  var pageCountEl = document.getElementById("pdf-page-count");
  var zoomLabel = document.getElementById("pdf-zoom-label");
  var statusEl = document.getElementById("pdf-status");

  var pdfDoc = null;
  var currentPage = 1;
  var scale = 1.25;
  var rendering = false;
  var pendingPage = null;

  function renderFallback(reason) {
    if (statusEl) statusEl.textContent = reason || "Using native browser PDF viewer.";
    stage.innerHTML = "";
    var obj = document.createElement("object");
    obj.className = "cose-pdf-fallback";
    obj.type = "application/pdf";
    obj.data = pdfUrl;
    var p = document.createElement("p");
    p.style.padding = "1rem";
    p.textContent = "Your browser could not embed the PDF inline. ";
    var a = document.createElement("a");
    a.href = pdfUrl;
    a.textContent = "Download the Manuscript PDF directly";
    p.appendChild(a);
    obj.appendChild(p);
    stage.appendChild(obj);
  }

  function renderPage(num) {
    if (!pdfDoc) return;
    rendering = true;
    pdfDoc.getPage(num).then(function (page) {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var viewport = page.getViewport({ scale: scale });
      var canvas = stage.querySelector("canvas") || document.createElement("canvas");
      var ctx = canvas.getContext("2d");
      canvas.width = Math.floor(viewport.width * dpr);
      canvas.height = Math.floor(viewport.height * dpr);
      canvas.style.width = Math.floor(viewport.width) + "px";
      canvas.style.height = Math.floor(viewport.height) + "px";
      if (!canvas.parentNode) {
        stage.innerHTML = "";
        stage.appendChild(canvas);
      }

      var task = page.render({
        canvasContext: ctx,
        transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null,
        viewport: viewport,
      });
      return task.promise;
    }).then(function () {
      rendering = false;
      if (pageInput) pageInput.value = String(currentPage);
      if (zoomLabel) zoomLabel.textContent = Math.round(scale * 100) + "%";
      if (statusEl) statusEl.textContent = "Page " + currentPage + " of " + pdfDoc.numPages;
      if (pendingPage !== null) {
        var next = pendingPage;
        pendingPage = null;
        renderPage(next);
      }
    }).catch(function () {
      rendering = false;
      renderFallback("PDF.js canvas rendering failed; switched to native PDF embed.");
    });
  }

  function queueRender(num) {
    currentPage = Math.max(1, Math.min(num, pdfDoc.numPages));
    if (rendering) pendingPage = currentPage;
    else renderPage(currentPage);
  }

  document.getElementById("pdf-prev")?.addEventListener("click", function () {
    if (pdfDoc && currentPage > 1) queueRender(currentPage - 1);
  });
  document.getElementById("pdf-next")?.addEventListener("click", function () {
    if (pdfDoc && currentPage < pdfDoc.numPages) queueRender(currentPage + 1);
  });
  pageInput?.addEventListener("change", function () {
    if (!pdfDoc) return;
    var val = parseInt(pageInput.value, 10);
    if (!Number.isNaN(val)) queueRender(val);
  });
  document.getElementById("pdf-zoom-in")?.addEventListener("click", function () {
    if (!pdfDoc) return;
    scale = Math.min(2.6, +(scale + 0.2).toFixed(2));
    queueRender(currentPage);
  });
  document.getElementById("pdf-zoom-out")?.addEventListener("click", function () {
    if (!pdfDoc) return;
    scale = Math.max(0.6, +(scale - 0.2).toFixed(2));
    queueRender(currentPage);
  });
  document.getElementById("pdf-fit")?.addEventListener("click", function () {
    if (!pdfDoc) return;
    pdfDoc.getPage(currentPage).then(function (page) {
      var base = page.getViewport({ scale: 1 });
      var avail = Math.max(300, stage.clientWidth - 48);
      scale = +(avail / base.width).toFixed(2);
      queueRender(currentPage);
    });
  });
  document.getElementById("pdf-fullscreen")?.addEventListener("click", function () {
    if (container.requestFullscreen) container.requestFullscreen().catch(function () {});
  });

  import("https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs")
    .then(function (pdfjsLib) {
      pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs";
      return pdfjsLib.getDocument(pdfUrl).promise;
    })
    .then(function (doc) {
      pdfDoc = doc;
      if (pageCountEl) pageCountEl.textContent = "/ " + doc.numPages;
      if (pageInput) pageInput.max = String(doc.numPages);
      renderPage(1);
    })
    .catch(function () {
      renderFallback("Loaded native PDF embed.");
    });
})();
