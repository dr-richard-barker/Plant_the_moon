/* Interactive Multi-Stage Stakeholder Presentation Deck Controller */
(function () {
  "use strict";

  var deck = document.getElementById("cose-stakeholder-deck");
  if (!deck) return;

  var allSlides = Array.prototype.slice.call(deck.querySelectorAll(".cose-slide"));
  var stageBtns = Array.prototype.slice.call(deck.querySelectorAll("[data-stage-filter]"));
  var prevBtn = document.getElementById("deck-prev");
  var nextBtn = document.getElementById("deck-next");
  var counterEl = document.getElementById("deck-counter");
  var progressFill = document.getElementById("deck-progress-fill");
  var notesToggle = document.getElementById("deck-notes-toggle");
  var fullscreenBtn = document.getElementById("deck-fullscreen");
  var statusEl = document.getElementById("deck-status");

  var activeStage = "all";
  var activeSlides = allSlides.slice();
  var currentIdx = 0;
  var showNotes = true;

  function syncView() {
    allSlides.forEach(function (s) {
      s.hidden = true;
    });
    if (!activeSlides.length) return;
    currentIdx = Math.max(0, Math.min(currentIdx, activeSlides.length - 1));
    var currentSlide = activeSlides[currentIdx];
    currentSlide.hidden = false;

    var notes = currentSlide.querySelector(".cose-speaker-notes");
    if (notes) notes.hidden = !showNotes;

    var label = "Slide " + (currentIdx + 1) + " / " + activeSlides.length;
    if (counterEl) counterEl.textContent = label;
    if (prevBtn) prevBtn.disabled = currentIdx === 0;
    if (nextBtn) nextBtn.disabled = currentIdx === activeSlides.length - 1;
    if (progressFill) {
      var pct = ((currentIdx + 1) / activeSlides.length) * 100;
      progressFill.style.width = pct.toFixed(1) + "%";
    }
    var h = currentSlide.querySelector("h2, h3");
    if (statusEl) {
      statusEl.textContent = label + (h ? ": " + h.textContent.trim() : "");
    }
  }

  function setStage(stage) {
    activeStage = stage;
    stageBtns.forEach(function (b) {
      var match = b.dataset.stageFilter === stage;
      b.setAttribute("aria-pressed", match ? "true" : "false");
    });
    activeSlides = allSlides.filter(function (s) {
      return stage === "all" || s.dataset.stage === stage;
    });
    currentIdx = 0;
    syncView();
  }

  stageBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      setStage(btn.dataset.stageFilter);
    });
  });

  prevBtn?.addEventListener("click", function () {
    if (currentIdx > 0) {
      currentIdx--;
      syncView();
    }
  });
  nextBtn?.addEventListener("click", function () {
    if (currentIdx < activeSlides.length - 1) {
      currentIdx++;
      syncView();
    }
  });

  notesToggle?.addEventListener("click", function () {
    showNotes = !showNotes;
    notesToggle.setAttribute("aria-pressed", showNotes ? "true" : "false");
    notesToggle.textContent = showNotes ? "Hide Speaker Notes" : "Show Speaker Notes";
    syncView();
  });

  fullscreenBtn?.addEventListener("click", function () {
    if (deck.requestFullscreen) deck.requestFullscreen().catch(function () {});
  });

  document.addEventListener("keydown", function (e) {
    if (e.target && /input|select|textarea/i.test(e.target.tagName)) return;
    if (e.key === "ArrowRight") {
      if (currentIdx < activeSlides.length - 1) {
        currentIdx++;
        syncView();
      }
    } else if (e.key === "ArrowLeft") {
      if (currentIdx > 0) {
        currentIdx--;
        syncView();
      }
    }
  });

  setStage("all");
})();
