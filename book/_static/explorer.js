/* CoSE Plant the Moon Interactive Report & Trial Explorer */
(function () {
  "use strict";

  var rootEl = document.getElementById("cose-explorer");
  if (!rootEl) return;

  var dataUrl = rootEl.dataset.jsonUrl;
  var tbody = document.getElementById("explorer-tbody");
  var table = document.getElementById("explorer-table");
  var statusEl = document.getElementById("explorer-status");
  var countBadge = document.getElementById("explorer-count");
  var dialog = document.getElementById("report-dialog");
  var dialogBody = document.getElementById("dialog-body");
  var dialogTitle = document.getElementById("dialog-team-title");

  var qInput = document.getElementById("f-search");
  var fSeason = document.getElementById("f-season");
  var fBody = document.getElementById("f-body");
  var fGuild = document.getElementById("f-guild");
  var fPdfOnly = document.getElementById("f-pdf-only");

  var collator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });
  var records = [];

  // Fallback light-dismiss for browsers without <dialog closedby="any">
  if (dialog && !("closedBy" in HTMLDialogElement.prototype)) {
    var pressedOutside = false;
    var outside = function (e) {
      var r = dialog.getBoundingClientRect();
      return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
    };
    dialog.addEventListener("pointerdown", function (e) { pressedOutside = outside(e); });
    dialog.addEventListener("pointerup", function (e) {
      if (pressedOutside && outside(e)) dialog.close();
    });
  }
  dialog?.addEventListener("close", function () {
    dialog.returnValue = "";
  });

  function populateSelect(sel, values) {
    var sorted = Array.from(new Set(values.filter(Boolean))).sort(collator.compare);
    sorted.forEach(function (v) {
      var opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      sel.appendChild(opt);
    });
  }

  function openReportDialog(rec) {
    if (!dialog || !dialogBody || !dialogTitle) return;
    dialogTitle.textContent = rec.team_name + " (" + rec.season + ")";
    dialogBody.innerHTML = "";

    var meta = document.createElement("p");
    meta.innerHTML = "";
    var badges = [
      rec.division_norm,
      rec.award_badges || rec.award_tier,
      rec.celestial_body ? "Target: " + rec.celestial_body : null,
      rec.regolith_simulant && rec.regolith_simulant !== "unspecified" ? "Simulant: " + rec.regolith_simulant : null,
      rec.crop_common_name && rec.crop_common_name !== "unspecified" ? "Crop: " + rec.crop_common_name : null,
      rec.crop_ncbitaxon ? rec.crop_ncbitaxon : null,
    ].filter(Boolean);
    badges.forEach(function (b) {
      var chip = document.createElement("span");
      chip.className = "cose-chip";
      chip.style.marginRight = "0.35rem";
      chip.style.marginBottom = "0.35rem";
      chip.textContent = b;
      meta.appendChild(chip);
    });
    dialogBody.appendChild(meta);

    if (rec.project_title) {
      var pt = document.createElement("p");
      pt.innerHTML = "";
      var strong = document.createElement("strong");
      strong.textContent = rec.project_title;
      pt.appendChild(strong);
      dialogBody.appendChild(pt);
    }

    if (rec.summary_findings) {
      var sum = document.createElement("p");
      sum.textContent = rec.summary_findings;
      dialogBody.appendChild(sum);
    }

    if (rec.pdf_url) {
      var linkRow = document.createElement("div");
      linkRow.className = "cose-btn-row";
      linkRow.style.marginBottom = "1rem";
      var a = document.createElement("a");
      a.className = "cose-btn primary";
      a.href = rec.pdf_url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "Open Original Student PDF (" + (rec.page_count || "?") + " pp.) →";
      linkRow.appendChild(a);
      dialogBody.appendChild(linkRow);
    }

    var arms = rec.arms || [];
    if (arms.length) {
      var h3 = document.createElement("h3");
      h3.textContent = "Extracted Experimental Arms (" + arms.length + ")";
      dialogBody.appendChild(h3);

      arms.forEach(function (arm) {
        var card = document.createElement("div");
        card.className = "cose-arm-card";
        var title = document.createElement("strong");
        title.textContent = (arm.arm_label || arm.amendment_category) + " · Outcome: " + arm.outcome_vs_regolith_control;
        card.appendChild(title);

        var metrics = [];
        if (arm.germination_rate_pct != null) metrics.push("Germination: " + arm.germination_rate_pct + "%");
        if (arm.mean_shoot_height_cm != null) metrics.push("Height: " + arm.mean_shoot_height_cm + " cm");
        if (arm.mean_fresh_biomass_g != null) metrics.push("Biomass: " + arm.mean_fresh_biomass_g + " g");
        if (metrics.length) {
          var mp = document.createElement("div");
          mp.style.fontSize = "0.84rem";
          mp.style.marginTop = "0.25rem";
          mp.textContent = metrics.join(" · ");
          card.appendChild(mp);
        }
        if (arm.evidence_quote) {
          var q = document.createElement("div");
          q.className = "cose-quote";
          q.textContent = "“" + arm.evidence_quote + "”" + (arm.page_number ? " (p. " + arm.page_number + ")" : "");
          card.appendChild(q);
        }
        dialogBody.appendChild(card);
      });
    }

    dialog.showModal();
  }

  function applyFilters() {
    var q = (qInput.value || "").trim().toLowerCase();
    var sVal = fSeason.value;
    var bVal = fBody.value;
    var gVal = fGuild.value;
    var pdfOnly = fPdfOnly.checked;

    var shown = 0;
    Array.prototype.forEach.call(tbody.rows, function (tr) {
      var rec = records[Number(tr.dataset.idx)];
      var ok =
        (!sVal || rec.season === sVal) &&
        (!bVal || rec.celestial_body === bVal) &&
        (!gVal || rec.crop_guild === gVal) &&
        (!pdfOnly || rec.has_pdf) &&
        (!q || tr.dataset.search.indexOf(q) !== -1);
      tr.hidden = !ok;
      if (ok) shown++;
    });

    var msg = shown + " / " + records.length + " records";
    if (countBadge) countBadge.textContent = msg;
    if (statusEl) statusEl.textContent = "Showing " + msg;
  }

  // Sortable table (reorders existing <tr> elements via moveBefore / appendChild)
  table?.addEventListener("click", function (e) {
    var btn = e.target.closest("th > button.sort-btn");
    if (!btn) return;
    var th = btn.closest("th");
    var dir = th.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";
    Array.prototype.forEach.call(table.tHead.rows[0].cells, function (h) {
      h.removeAttribute("aria-sort");
    });
    th.setAttribute("aria-sort", dir);

    var idx = th.cellIndex;
    var type = th.dataset.type || "text";
    var factor = dir === "ascending" ? 1 : -1;
    var rows = Array.prototype.slice.call(tbody.rows);

    rows.sort(function (a, b) {
      var va = a.cells[idx].dataset.value ?? a.cells[idx].textContent.trim();
      var vb = b.cells[idx].dataset.value ?? b.cells[idx].textContent.trim();
      if (type === "number") return factor * (Number(va) - Number(vb));
      return factor * collator.compare(va, vb);
    });

    rows.forEach(function (row) {
      if (typeof tbody.moveBefore === "function") tbody.moveBefore(row, null);
      else tbody.appendChild(row);
    });
    if (statusEl) statusEl.textContent = "Sorted by " + btn.textContent.trim() + ", " + dir;
  });

  fetch(dataUrl)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      records = data;
      populateSelect(fSeason, data.map(function (d) { return d.season; }));
      populateSelect(fBody, data.map(function (d) { return d.celestial_body; }));
      populateSelect(fGuild, data.map(function (d) { return d.crop_guild; }));

      var frag = document.createDocumentFragment();
      data.forEach(function (rec, idx) {
        var tr = document.createElement("tr");
        tr.dataset.idx = String(idx);
        tr.dataset.search = [
          rec.team_name, rec.season, rec.project_title, rec.crop_common_name,
          rec.regolith_simulant, rec.amendment_categories, rec.location_state,
        ].filter(Boolean).join(" ").toLowerCase();

        var cells = [
          { label: "Season", text: rec.season, val: String(rec.season_order || 0) },
          { label: "Team", text: rec.team_name, isHeader: true },
          { label: "Target", text: rec.celestial_body || "—" },
          { label: "Crop", text: rec.crop_common_name || "—" },
          { label: "Amendments", text: (rec.amendment_categories || "—").replace(/_/g, " ") },
          { label: "PDF", text: rec.has_pdf ? "PDF (" + (rec.page_count || "?") + "p)" : "Award only", val: rec.has_pdf ? "1" : "0" },
        ];

        cells.forEach(function (c) {
          var el = document.createElement(c.isHeader ? "th" : "td");
          if (c.isHeader) el.scope = "row";
          el.dataset.label = c.label;
          if (c.val !== undefined) el.dataset.value = c.val;
          if (c.isHeader) {
            var b = document.createElement("button");
            b.type = "button";
            b.className = "cose-btn";
            b.style.padding = "0.2rem 0.6rem";
            b.style.fontSize = "0.84rem";
            b.textContent = c.text;
            b.addEventListener("click", function () { openReportDialog(rec); });
            el.appendChild(b);
          } else {
            el.textContent = c.text;
          }
          tr.appendChild(el);
        });
        frag.appendChild(tr);
      });
      tbody.appendChild(frag);
      applyFilters();
    });

  [qInput, fSeason, fBody, fGuild, fPdfOnly].forEach(function (el) {
    el?.addEventListener("input", applyFilters);
    el?.addEventListener("change", applyFilters);
  });
})();
