# 187-Report & Trial Arm Explorer

Filter all **324 Plant the Moon Challenge award records** (`187` PDF reports + `137` metadata-only State & NASA Space Grant entries) across `Spring 2021`–`Spring 2026`. Click any team name to inspect its extracted experimental parameters, trial arms, and verbatim page-cited PDF provenance quotes.

<div id="cose-explorer" data-json-url="_static/data/cose_ptm_explorer.json">
  <div class="cose-filter-bar" role="search" aria-label="Filter Plant the Moon reports">
    <label>Keyword Search
      <input type="search" id="f-search" placeholder="Team, crop, simulant, amendment…">
    </label>
    <label>Season
      <select id="f-season"><option value="">All Seasons</option></select>
    </label>
    <label>Celestial Body
      <select id="f-body"><option value="">All Targets</option></select>
    </label>
    <label>Crop Guild
      <select id="f-guild"><option value="">All Guilds</option></select>
    </label>
    <label style="justify-content:flex-end;">
      <span><input type="checkbox" id="f-pdf-only" checked> PDF Reports Only (187)</span>
      <span id="explorer-count" class="cose-chip" style="margin-top:0.3rem;">Loading…</span>
    </label>
  </div>

  <div id="explorer-status" class="cose-sr-only" role="status"></div>

  <div tabindex="0" role="region" aria-labelledby="explorer-table-caption" class="cose-table-wrapper">
    <table id="explorer-table" class="cose-table">
      <caption id="explorer-table-caption" class="cose-sr-only">
        Plant the Moon Challenge scraped awards and extracted experimental summaries
      </caption>
      <thead>
        <tr>
          <th scope="col" data-type="number"><button type="button" class="sort-btn">Season</button></th>
          <th scope="col" data-type="text"><button type="button" class="sort-btn">Team (Inspect)</button></th>
          <th scope="col" data-type="text"><button type="button" class="sort-btn">Target</button></th>
          <th scope="col" data-type="text"><button type="button" class="sort-btn">Crop</button></th>
          <th scope="col" data-type="text"><button type="button" class="sort-btn">Amendments</button></th>
          <th scope="col" data-type="number"><button type="button" class="sort-btn">PDF</button></th>
        </tr>
      </thead>
      <tbody id="explorer-tbody"></tbody>
    </table>
  </div>

  <dialog id="report-dialog" class="cose-dialog" closedby="any" aria-labelledby="dialog-team-title">
    <div class="cose-dialog-head">
      <h2 id="dialog-team-title" style="margin:0;">Report Details</h2>
      <form method="dialog">
        <button class="cose-btn" value="close" autofocus>Close ✕</button>
      </form>
    </div>
    <div id="dialog-body"></div>
  </dialog>
</div>

<script src="_static/explorer.js"></script>
