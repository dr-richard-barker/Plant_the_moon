#let data = json("/manuscript/manuscript_data.json")

#set document(
  title: "FAIR AI/ML Meta-Analysis of Student Regolith Plant-Growth Research Across the Plant the Moon Challenge (2021–2026)",
  author: "Richard J. Barker",
)

#set page(
  paper: "us-letter",
  margin: (x: 0.7in, y: 0.72in),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 7.8pt, fill: rgb("#5f7f8a"))
      #grid(
        columns: (1fr, auto),
        [Barker (2026) · CoSE FAIR Meta-Analysis of the Plant the Moon Challenge (2021–2026)],
        [Page #counter(page).display()],
      )
      #v(-4pt)
      #line(length: 100%, stroke: 0.45pt + rgb("#cfdde1"))
    ]
  },
  footer: context [
    #set text(size: 7.5pt, fill: rgb("#5f7f8a"))
    #line(length: 100%, stroke: 0.4pt + rgb("#cfdde1"))
    #grid(
      columns: (1fr, auto),
      [Collaborative Science Environment (CoSE) · `https://dr-richard-barker.github.io/Plant_the_moon/`],
      [ORCID: 0000-0001-5681-9857 · MIT / CC-BY-4.0],
    )
  ],
)

#set text(font: ("Helvetica Neue", "Arial"), size: 9.5pt, fill: rgb("#0f2a33"))
#set par(justify: true, leading: 0.56em)
#set heading(numbering: "1.1")

#show heading: it => {
  set text(fill: rgb("#004053"), weight: "bold")
  v(0.55em)
  it
  v(0.22em)
}

// =========================================================================
// Title & Affiliation Header Banner
// =========================================================================
#box(
  width: 100%,
  fill: rgb("#eaf1f3"),
  stroke: (left: 4.5pt + rgb("#004053")),
  inset: 14pt,
  radius: 4pt,
)[
  #text(size: 8pt, fill: rgb("#0f7f9f"), weight: "bold")[COLLABORATIVE SCIENCE ENVIRONMENT (CoSE) · RESEARCH SYNTHESIS MANUSCRIPT]
  #v(0.3em)
  #text(size: 15.5pt, weight: "bold", fill: rgb("#004053"))[
    FAIR AI/ML Meta-Analysis of Student Regolith Plant-Growth Research Across the Plant the Moon Challenge (2021–2026)
  ]
  #v(0.4em)
  #text(size: 9.4pt, fill: rgb("#0f2a33"))[
    *Richard J. Barker, PhD*#super[1,2,3\*]
  ]
  #v(0.2em)
  #text(size: 8.2pt, fill: rgb("#3d5a64"))[
    #super[1]Collaborative Science Environment (CoSE) Benefit Corp & AstroBotany.com, Madison, WI, USA ·
    #super[2]Chair, NASA GeneLab / OSDR Plant Analysis Working Group ·
    #super[3]Science Co-Lead, NASA Lunar LEAF (Purdue University) \
    #super[\*]Correspondence: `dr.richard.barker@gmail.com` · ORCID: `https://orcid.org/0000-0001-5681-9857` · Code & Data: `https://github.com/dr-richard-barker/Plant_the_moon`
  ]
]

#v(0.55em)

// =========================================================================
// Structured Abstract
// =========================================================================
#box(
  width: 100%,
  stroke: 0.75pt + rgb("#cfdde1"),
  inset: 11pt,
  radius: 4pt,
)[
  #text(size: 9pt)[
    *Abstract* \
    *Background:* Sustaining crop production in extraterrestrial regolith is a foundational requirement for bioregenerative life support systems (BLSS) on the Moon and Mars. While landmark laboratory studies using authentic Apollo lunar samples and standardized regolith simulants have identified severe ionic, alkaline, reactive oxygen species (ROS), and hydraulic stresses, broad combinatorial screening of organic, microbial, and polymeric substrate interventions remains fragmented across educational and citizen-science networks. Over twelve competition seasons (`Spring 2021`–`Spring 2026`), student and university teams participating in the *Plant the Moon Challenge* have generated a large, distributed experimental archive testing diverse crop guilds and regolith amendments. \
    *Methods:* We engineered `ptm-meta`, an automated, FAIR-compliant (Findable, Accessible, Interoperable, Reusable) acquisition, provenance, and machine-learning pipeline. The pipeline crawls all `24` archived awards pages (`#data.total_award_entries` total award entries), verifies `#data.total_pdf_reports` full-text student PDF reports via SHA-256 checksums (`#data.total_pages` pages; `#data.total_tables` extracted tables), extracts `#data.total_arms` structured trial arms (`#data.total_treatment_arms` experimental treatment arms and `205` baseline controls) under a strict Draft 2020-12 JSON Schema with verbatim page-cited provenance quotes, and maps biological taxa and substrate interventions to OBO Foundry ontologies (`NCBITaxon`, `ENVO`, `AGRO`, `CHEBI`, `PECO`) packaged within an RO-Crate 1.1 research object. \
    *Results:* Across `#data.total_pdf_reports` PDF reports, `#data.celestial_counts.at("lunar", default: 0)` (`70.6%`) target lunar regolith simulants, `#data.celestial_counts.at("martian", default: 0)` (`25.1%`) target Martian simulants, and `#data.celestial_counts.at("both", default: 0)` (`3.2%`) compare both substrates. Taxonomic harmonization mapped `#data.ncbitaxon_mapped` reports (`#data.ncbitaxon_pct%`) to NCBI Taxonomy identifiers, dominated by *Raphanus sativus* (`n = 34`), *Phaseolus vulgaris* (`n = 19`), *Spinacia oleracea* (`n = 16`), *Lactuca sativa* (`n = 14`), and *Pisum sativum* (`n = 12`). Unsupervised TF-IDF + SVD + UMAP projection identified coherent experimental archetypes stratified by celestial target, division track, and amendment paradigm. Under leak-free `StratifiedGroupKFold` cross-validation grouped strictly by `report_id` (`#data.ml.n_total_arms` scored arms across `#data.ml.n_unique_reports` unique reports), a Random Forest classifier achieved CV ROC-AUC of `#data.ml.models.at(2).cv_roc_auc` (95% bootstrap CI: `#data.ml.models.at(2).cv_roc_auc_ci.at(0)`–`#data.ml.models.at(2).cv_roc_auc_ci.at(1)`) and CV PR-AUC of `#data.ml.models.at(2).cv_pr_auc`, outperforming the majority-class baseline (`ROC-AUC = 0.500`). Microbial/mycorrhizal inoculants (`92.0%` improved, 95% Wilson CI: `75.0–97.8%`), vermicompost/aquaculture effluents (`100.0%`, `72.2–100.0%`), organic compost (`80.0%`, `60.9–91.1%`), and coir/peat/perlite structural matrices (`77.3%`, `56.6–89.9%`) demonstrated the most consistent positive growth responses relative to unamended regolith controls. \
    *Conclusions:* Amending regolith succeeds most reliably when biological nutrient mobilization (microbial necromass, mycorrhizae, vermicompost) is paired with physical pore-structure and pH buffering matrices. To maximize scientific reuse of student astro-agricultural trials, future cohorts should mandate paired 100% unamended regolith negative controls (currently `#data.reg_ctrl_pct%`) alongside terrestrial soil controls (`#data.earth_ctrl_pct%`) and standardized replicate-level tabular reporting.
  ]
]

#v(0.45em)

// KPI Strip
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 8pt,
  ..(("Award Entries / PDFs", str(data.total_award_entries) + " / " + str(data.total_pdf_reports)),
     ("Parsed Pages / Tables", str(data.total_pages) + " / " + str(data.total_tables)),
     ("Total / Treatment Arms", str(data.total_arms) + " / " + str(data.total_treatment_arms)),
     ("NCBITaxon Coverage", str(data.ncbitaxon_mapped) + " (" + str(data.ncbitaxon_pct) + "%)")).map(((lbl, val)) => box(
    width: 100%, fill: rgb("#f5f8f9"), stroke: 0.6pt + rgb("#cfdde1"), inset: 7pt, radius: 4pt,
  )[
    #text(size: 12pt, weight: "bold", fill: rgb("#004053"))[#val] \
    #text(size: 7.5pt, fill: rgb("#5f7f8a"))[#lbl]
  ])
)

= Introduction

Sustained human exploration beyond low Earth orbit (LEO) under NASA's Artemis lunar architecture and future crewed Mars missions requires transitioning from cargo-resupplied rations to closed-loop bioregenerative life support systems (BLSS) @wheeler2017agriculture. Higher plants play a dual physiological role in planetary habitats: fixing atmospheric carbon dioxide into edible caloric and micronutrient biomass while recycling potable water via canopy transpiration and generating photosynthetically derived oxygen @wheeler2017agriculture @barker2020toast. However, transporting bulk horticultural media out of Earth's gravity well is mass-prohibitive for large-scale crop production. Consequently, in-situ resource utilization (ISRU)—converting indigenous lunar and Martian regolith into biologically functional growth substrates—has emerged as a major research priority across astrobotany and planetary engineering @paul2022plants @wamelink2014can.

Authentic extraterrestrial regolith presents severe physicochemical and biological barriers to plant development. In a landmark transcriptomic and phenotypic study using authentic Apollo 11, 12, and 17 lunar regolith samples, Paul, Elardo, and Ferl demonstrated that while *Arabidopsis thaliana* seeds germinate readily on lunar regolith, post-germination seedlings exhibit severe root stunting, anthocyanin accumulation, and broad differential expression of stress-response genes associated with reactive oxygen species (ROS), salt, ionic, and heavy-metal toxicity @paul2022plants. Furthermore, growth inhibition scaled directly with regolith maturity and cosmic-weathering exposure (nanophase metallic iron and agglutinate abundance) @paul2022plants. Because authentic lunar samples are strictly limited, earthbound research relies on high-fidelity mineralogical and geomechanical simulants, notably Lunar Highlands Simulant (`LHS-1`), Lunar Mare Simulant (`LMS-1`) @longfox2023geomechanical, and Mars Global Simulant (`MGS-1`, modeled on the Curiosity rover's Rocknest basaltic soil stoichiometry) @cannon2019mars. Controlled glasshouse trials comparing crop species across lunar and Martian simulants have shown that unamended regolith suffers from extreme nutrient deficiency (virtual absence of bioavailable reactive nitrogen and organic carbon), poor water retention or surface crusting due to angular fine silt/dust particle-size distributions, and alkaline pH (often pH 8.5–10.0 in anorthositic/basaltic simulants) that precipitates micronutrients @wamelink2014can @longfox2023geomechanical @cannon2019mars.

While individual university laboratories typically evaluate one crop species and a single amendment factor at a time, participatory citizen-science and student research networks provide a massive, parallelized screening engine across heterogeneous environmental conditions. Since 2021, the *Plant the Moon Challenge* (PTMC), administered by the Institute of Competition Sciences (ICS) in partnership with Space Grant consortia and Exolith Lab, has engaged thousands of Elementary, Middle, High School, and Professional/University student teams worldwide in 8- to 10-week regolith cultivation experiments @ics2026ptm. Each season, top-performing teams publish detailed experimental reports spanning novel organic waste streams, microbial/mycorrhizal consortia, biopolymer hydrogels, and spectral lighting regimes.

Despite its scientific and pedagogical value, the PTMC archive has historically existed as an unstructured collection of WordPress web pages and heterogeneous PDF documents—ranging from formal scientific papers to classroom slide decks and scanned posters—lacking machine-actionable metadata, standardized taxonomic identifiers, or cross-season synthesis. Just as NASA's Open Science Data Repository (OSDR) and the Test of *Arabidopsis* Space Transcriptome (TOAST) database transformed fragmented spaceflight omics experiments into FAIR (Findable, Accessible, Interoperable, Reusable) discovery platforms @barker2020toast @scott2024nasa @wilkinson2016fair, transforming student regolith trials into a schema-validated, ontology-linked knowledge base enables systematic meta-analysis. Here we present the design, validation, and empirical findings of `ptm-meta`, a complete FAIR data acquisition and machine-learning synthesis of the 2021–2026 Plant the Moon Challenge archive.

= Materials and Methods

== Archive Acquisition and SHA-256 Provenance Tracking

We configured `ptm-meta` (`configs/seasons.yaml`) to crawl all `24` official awards archive endpoints on `plantthemoon.com` spanning twelve consecutive competition seasons from `Spring 2021` through `Spring 2026`, covering both the Main track (`/awards-<season>/`, High School and Professional/University divisions) and the Junior track (`/jr/awards-<season>/`, Elementary and Middle School divisions) @ics2026ptm. Raw HTML snapshots were archived locally for deterministic offline verification.

An Elementor-aware DOM parser (`src/ptm_meta/scrape.py`) extracted award cards across three distinct recognition tiers: (1) *Best in Show* national/international category winners (which include direct hyperlinks to full-text PDF project reports), (2) *State Award* winners (`Top <State> Team`), and (3) *NASA Space Grant Regional Expansion Project* winners. The scraper automatically repaired Windows-1252/UTF-8 mojibake sequences embedded in legacy WordPress entries, resolved multi-line `<br>` team headings, and deduplicated teams winning multiple honors within the same season by merging their recognition badges into a unified `award_badges` array while preserving canonical source URLs. Each record received a deterministic primary key (`report_id`) constructed from its season slug, track, normalized team name, and a 6-character SHA-1 URL digest.

All linked PDF files (`n = #data.total_pdf_reports`) were fetched concurrently via `httpx` with exponential-backoff retry logic (`src/ptm_meta/fetch.py`). For every downloaded file, the pipeline computed a 64-character hexadecimal SHA-256 digest, exact byte size, HTTP status code, UTC acquisition timestamp, and `PyMuPDF` page count, writing a machine-validated provenance manifest (`data/raw/manifest.{csv,json}`) conforming to `schemas/report_manifest.schema.json`.

== PDF Text, Layout, and Table Extraction

Each verified PDF was processed through a two-stage parser (`src/ptm_meta/pdf_parse.py`):
1. *Page-level text and image census (`PyMuPDF` v2.1):* Extracted normalized text strings, character counts, and embedded raster image counts for every page (`#data.total_pages` total pages; `3,425,506` characters).
2. *Structured table extraction (`pdfplumber` v0.11):* Extracted cell-level tabular matrices (`#data.total_tables` total tables across the corpus) from the first 30 pages of each report, normalizing whitespace and filtering empty decorative grids.

Reports were classified into three diagnostic parse-quality tiers based on average character density per page: `digital_text` (`>= 150` chars/page; `n = #data.digital_text_pdfs`), `sparse_text` (`20–149` chars/page; `n = 0`), and `image_or_scanned` (`< 20` chars/page; `n = #data.scanned_pdfs`, specifically `fall23-main-kca-moon-planters-ed532e` and `spring25-junior-the-lunar-league-c7d132`).

== Schema-Enforced Hybrid Extraction and Quote Verification

To accommodate both zero-credential offline reproducibility and high-recall multimodal LLM extraction, `src/ptm_meta/extract.py` enforces a strict Pydantic v2 data model (`ReportExtraction` and `TrialArm`, mirrored in `schemas/experiment_record.schema.json`) across two pluggable backends:
- *Table-Aware Deterministic Heuristic Backend (`--backend heuristic`):* Uses weighted title/early-page regular-expression scoring to classify celestial target (`lunar`, `martian`, `both`, `unspecified`) without being confounded by general space-exploration background sections; resolves regolith simulant codes (`LHS-1`, `LHS-1D`, `LMS-1`, `JSC-1A`, `MGS-1`, `MMS-1`, `MMS-2`, and Exolith Lab synonyms); identifies focal crop taxa and functional guilds; detects terrestrial positive controls, unamended 100% regolith negative controls, and formal statistical hypothesis tests (`ANOVA`, `t-test`, `Tukey HSD`, `Chi-square`, linear regression, `p`-values); scans extracted `pdfplumber` tables for numeric endpoints (`germination_rate_pct`, `mean_shoot_height_cm`, `mean_fresh_biomass_g`, `substrate_ph`); and evaluates local text windows (`±300` characters) around each detected amendment to assign outcome direction (`improved`, `neutral`, `reduced`, `not_reported`) alongside a verbatim `evidence_quote` and 1-based `page_number`.
- *Gemini Multimodal Structured Backend (`--backend gemini`):* Sends page-indexed text, JSON tables, and—for `image_or_scanned` or chart-only reports—native `application/pdf` byte streams to `gemini-2.5-flash` with `response_schema=ReportExtraction` at `temperature = 0.1`.

Every extraction undergoes an automated provenance audit (`verify_quote_provenance()`) that normalizes whitespace and verifies whether each extracted `evidence_quote` substring appears verbatim in the parsed PDF text layer.

== FAIR Packaging and OBO Foundry Ontology Harmonization

To satisfy the FAIR Guiding Principles @wilkinson2016fair, `src/ptm_meta/ontologies.py` and `src/ptm_meta/normalize.py` map extracted strings to persistent Open Biological and Biomedical Ontology (OBO) Foundry Uniform Resource Identifiers (URIs):
- *Botanical & Fungal Taxa (`NCBITaxon`):* Mapped 30 crop species to canonical NCBI Taxonomy identifiers (e.g., *Raphanus sativus* `NCBITaxon:3726`, *Lactuca sativa* `NCBITaxon:4236`, *Spinacia oleracea* `NCBITaxon:3562`, *Phaseolus vulgaris* `NCBITaxon:3885`, *Pisum sativum* `NCBITaxon:3888`, *Pleurotus ostreatus* `NCBITaxon:5322`).
- *Amendments & Environmental Conditions (`ENVO`, `AGRO`, `CHEBI`, `PECO`):* Crosswalked all 14 standardized amendment categories to Agronomy Ontology (`AGRO:00000370` microbial/mycorrhizal inoculant; `AGRO:00000338` vermicompost; `AGRO:00000337` biochar; `AGRO:00000315` synthetic NPK), Environment Ontology (`ENVO:00002149` compost; `ENVO:00001998` soil; `ENVO:00005750` regolith), Chemical Entities of Biological Interest (`CHEBI:33285` hydrogel/alginate biopolymer), and Plant Experimental Conditions Ontology (`PECO:0007152` light spectrum).

All code, schemas, crosswalks (`data/processed/ontology_mappings.json`), tabular exports (CSV, Apache Parquet, JSON), notebooks, and the compiled manuscript are cataloged with SHA-256 checksums inside an *RO-Crate 1.1* metadata descriptor (`ro-crate-metadata.json`) @soilandreyes2022packaging, accompanied by `CITATION.cff` and `codemeta.json`.

== Unsupervised Clustering and Leak-Free Grouped Machine Learning

For unsupervised protocol mapping (`book/notebooks/02_unsupervised_clustering.ipynb`), report narratives (project title, key hypothesis, summary findings, and amendment categories) were vectorized via `TfidfVectorizer` (`max_features = 800`, 1–2 word n-grams), reduced via `TruncatedSVD` (`20` components), concatenated with one-hot-encoded categorical protocol descriptors (`celestial_body`, `regolith_simulant`, `crop_guild`, `track`), and standardized via `StandardScaler`. We swept K-Means (`k = 2..10`, `n_init = 20`) to maximize the mean Silhouette Score and projected the corpus into two dimensions using both Principal Component Analysis (PCA) and Uniform Manifold Approximation and Projection (`UMAP`, `n_neighbors = 15`, `min_dist = 0.15`).

For supervised predictive modeling (`src/ptm_meta/analysis.py` and `book/notebooks/03_meta_analysis_ml.ipynb`), we formulated a binary classification task predicting whether a non-control treatment arm achieved an `improved` growth outcome relative to unamended regolith (`target_improved = 1` vs. `neutral`/`reduced = 0`; `n = #data.ml.n_total_arms` scored arms across `#data.ml.n_unique_reports` unique reports). Because multiple treatment arms within a single report share common environmental conditions, team protocols, and baseline controls, standard random row splitting would induce severe *group data leakage*. We enforced two strict architectural safeguards:
1. *Report-Grouped Splitting:* A 20% hold-out test set (`#data.ml.n_test_arms` arms) was partitioned via `GroupShuffleSplit(test_size = 0.20, random_state = 42)` grouped on `report_id`, guaranteeing zero overlap of student reports between training (`#data.ml.n_train_arms` arms) and test sets. Model selection and out-of-fold probability estimation on the training split used 5-fold `StratifiedGroupKFold(n_splits = 5)` grouped on `report_id`.
2. *Training-Only Featurization:* All preprocessing (`SimpleImputer(strategy="median")` + `StandardScaler` for numerical features including explicit missingness indicator `missing_duration`; constant imputation + `OneHotEncoder(handle_unknown="ignore", max_categories=14)` for categorical features) was encapsulated inside an `sklearn.pipeline.Pipeline` and fit strictly inside each training fold.

We benchmarked four models: (1) `DummyClassifier(strategy="most_frequent")` naive baseline, (2) L2-regularized `LogisticRegression(C=0.5)`, (3) `RandomForestClassifier(n_estimators=200, max_depth=6)`, and (4) `HistGradientBoostingClassifier(max_depth=4, learning_rate=0.06)`. Out-of-fold ROC-AUC and PR-AUC were evaluated with 500-iteration percentile bootstrap 95% confidence intervals, subgroup slice diagnostics (`celestial_body` and `track`), and `TreeExplainer` SHAP global feature attributions.

= Results

== Longitudinal Archive Coverage and Division-Level Experimental Rigor

Across all `24` archived awards pages (`Spring 2021`–`Spring 2026`), `ptm-meta` indexed `#data.total_award_entries` unique team recognition records, comprising `#data.total_pdf_reports` full-text PDF reports and `137` metadata-only State Award and NASA Space Grant Regional Expansion records (Table 1). Best in Show PDF availability remained highly consistent at `15–18` reports per season from `Fall 2021` through `Spring 2026` (8 Main track + 7–8 Junior track reports per season, with 10 Main track reports in `Fall 2024` and `Spring 2025`), following the initial `Spring 2021` (`16` PDFs) and `Summer 2021` (`9` PDFs) launch cohorts.

#figure(
  table(
    columns: (1.5fr, 0.9fr, 0.9fr, 0.9fr, 0.9fr, 1.1fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Season*], [*Total Entries*], [*Total PDFs*], [*Main PDFs*], [*Junior PDFs*], [*State / Space Grant Only*],
    ..data.season_breakdown.map(s => (
      s.season,
      str(s.total_awards),
      str(s.pdf_reports),
      str(s.main_pdfs),
      str(s.junior_pdfs),
      str(s.meta_only),
    )).flatten()
  ),
  caption: [Chronological breakdown of scraped award records and SHA-256-verified PDF reports across 12 Plant the Moon Challenge seasons (`Spring 2021`–`Spring 2026`).],
)

Auditing experimental design rigor across student divisions revealed a pronounced methodological gradient between K–8 Junior cohorts and High School / Professional cohorts (Table 2; Figure 1). Overall, `#data.earth_ctrl_pct%` of PDF reports incorporated a terrestrial potting-soil or garden-soil positive control, whereas only `#data.reg_ctrl_pct%` explicitly reported a `100% unamended regolith` negative control arm, and `#data.stat_test_pct%` reported formal inferential statistical tests (`ANOVA`, *t*-tests, or `p`-values). Professional/University teams averaged `18.3` pages and `8.4` extracted tables per report with `29.6%` reporting formal statistical tests, compared to `15.7` pages (`20.8%` statistical testing) in High School reports, `13.4` pages (`4.3%` statistical testing) in Middle School reports, and `10.1` pages (`2.2%` statistical testing) in Elementary School reports.

#figure(
  table(
    columns: (1.8fr, 0.7fr, 0.9fr, 0.9fr, 1.1fr, 1.2fr, 1.1fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Normalized Division*], [*PDFs*], [*Mean Pages*], [*Mean Tables*], [*Earth Control*], [*100% Regolith Control*], [*Statistical Test*],
    ..data.division_rigor.map(d => (
      d.division,
      str(d.n_pdfs),
      str(d.mean_pages),
      str(d.mean_tables),
      str(d.earth_ctrl_pct) + "%",
      str(d.reg_ctrl_pct) + "%",
      str(d.stat_test_pct) + "%",
    )).flatten()
  ),
  caption: [Document complexity and experimental rigor indicators stratified by normalized student competition division (`n = 187` PDF reports).],
)

#if data.figures_present.fig1 [
  #figure(
    image("/manuscript/figures/fig1.png", width: 98%),
    caption: [(A) Archived PDF reports per competition season stratified by Main vs. Junior track. (B) Longitudinal trends in terrestrial positive control, unamended 100% regolith negative control, and formal statistical test adoption (`2021–2026`).],
  )
]

== Celestial Target Simulants and Taxonomic Crop Selection

Weighted title and early-page classification showed that `#data.celestial_counts.at("lunar", default: 0)` reports (`70.6%`) investigated lunar regolith simulants, `#data.celestial_counts.at("martian", default: 0)` (`25.1%`) investigated Martian regolith simulants (reflecting the companion *Plant Mars Challenge* seasonal track), `#data.celestial_counts.at("both", default: 0)` (`3.2%`) conducted comparative dual-simulant trials, and `#data.celestial_counts.at("unspecified", default: 0)` (`1.1%`) were scanned/unspecified submissions. Among reports explicitly naming their commercial simulant code in text, Exolith Lab's Lunar Highlands Simulant (`LHS-1`, `n = 19`) and Mars Global Simulant (`MGS-1`, `n = 14`) were the predominant open standards @longfox2023geomechanical @cannon2019mars, alongside general Exolith Lab citations (`n = 8`) and Mojave Mars Simulant (`MMS-1`, `n = 1`), while `145` reports referred generically to "lunar regolith simulant" or "Martian regolith simulant" supplied in the official PTMC kit.

Semantic harmonization mapped `#data.ncbitaxon_mapped / #data.total_pdf_reports` reports (`#data.ncbitaxon_pct%`) to specific focal crops with `NCBITaxon` identifiers (Table 3). Fast-germinating root crops, legumes, and leafy greens dominated student selection: radish (*Raphanus sativus*, `NCBITaxon:3726`, `18.2%` of all reports) was the single most popular model organism due to its rapid 3–5 day emergence and compact taproot biomass, followed by green/bush bean (*Phaseolus vulgaris*, `10.2%`), spinach (*Spinacia oleracea*, `8.6%`), lettuce (*Lactuca sativa*, `7.5%`), and pea (*Pisum sativum*, `6.4%`). Notably, five Professional and High School teams pioneered mycoponic and fungal biomanufacturing trials using oyster mushroom (*Pleurotus ostreatus*, `NCBITaxon:5322`) to simultaneously valorize lignocellulosic waste and bind loose regolith into structural biocomposites.

#figure(
  table(
    columns: (1.2fr, 1.5fr, 1.2fr, 1.1fr, 0.7fr, 0.8fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Common Name*], [*Scientific Name*], [*NCBI Taxonomy ID*], [*Crop Guild*], [*Reports*], [*Share*],
    ..data.top_crops.map(c => (
      c.crop,
      emph(c.scientific),
      raw(c.ncbitaxon),
      c.guild,
      str(c.count),
      str(c.pct) + "%",
    )).flatten()
  ),
  caption: [Top 10 focal crop species cultivated across the Plant the Moon Challenge archive (`2021–2026`), harmonized to OBO Foundry `NCBITaxon` identifiers.],
)

== Unsupervised Discovery of Experimental Protocol Archetypes

Combining TF-IDF + TruncatedSVD narrative embeddings with one-hot-encoded protocol features (`celestial_body`, `regolith_simulant`, `crop_guild`, `track`) and sweeping K-Means across `k = 2..10` identified meaningful latent structure in the 2D UMAP manifold (Figure 2). The UMAP projection cleanly partitions lunar vs. Martian experimental campaigns along its primary axis while grouping protocols by amendment strategy: (1) _Biological & Microbial Nitrogen/Phosphorus Mobilizers_ (arbuscular mycorrhizal fungi, _Rhizobium_ and _Bradyrhizobium_, _Azotobacter_, cyanobacteria, and sterilized microbial necromass), (2) _Organic & Circular Waste Valorization_ (compost, vermicompost, aquaculture effluent, human hair/urea analogs, and food-waste extracts), (3) _Physical Matrix & Hydraulic Conditioners_ (coco coir, sphagnum peat moss, perlite, vermiculite, sodium alginate spherification, and superabsorbent hydrogels), and (4) _Controlled-Environment Photobiology & Mineral Nano-Supplements_ (LED wavelength manipulation and banana-peel / mineral nano-fertilizers).

#if data.figures_present.fig2 [
  #figure(
    image("/manuscript/figures/fig2.png", width: 96%),
    caption: [2D UMAP manifold of all 187 PDF reports derived from joint TF-IDF + SVD semantic embeddings and encoded experimental protocol features, colored by (A) unsupervised K-Means cluster archetype and (B) target celestial body.],
  )
]

== Meta-Analysis of Amendment Efficacy and Leak-Free Predictive ML

Across all `#data.total_arms` extracted trial arms (`205` control arms: `134` terrestrial soil controls and `71` unamended 100% regolith controls; `#data.total_treatment_arms` experimental treatment arms), `#data.scored_treatment_arms` treatment arms contained sufficient local text or tabular evidence to score directional growth outcomes relative to unamended regolith controls (Table 4). Overall, `82.8%` (`106 / 128`) of scored treatment arms reported positive growth improvement over unamended regolith, whereas `16.4%` (`21 / 128`) reported growth reduction/inhibition (typically associated with over-application of concentrated synthetic salts, raw acidic waste, or hyper-absorbent polymer waterlogging).

Among major amendment classes ($n >= 10$ scored arms), *vermicompost and aquaculture waste effluents* (`10 / 10` arms, `100.0%`, 95% Wilson CI: `72.2–100.0%`) and *microbial/mycorrhizal bio-inoculants* (`23 / 25` arms, `92.0%`, 95% Wilson CI: `75.0–97.8%`) achieved the highest empirical success rates, followed by *organic compost/manure* (`20 / 25` arms, `80.0%`, `60.9–91.1%`), *synthetic NPK/hydroponic nutrient solutions* (`8 / 10` arms, `80.0%`, `49.0–94.3%`), and *coir/peat/perlite structural matrices* (`17 / 22` arms, `77.3%`, `56.6–89.9%`). Mineral and nano-fertilizer additions without organic buffering showed higher variance (`60.0%` improved, `31.3–83.2%`), frequently suffering from salinity or pH-induced nutrient lockup when applied directly to 100% regolith simulant.

#figure(
  table(
    columns: (2.2fr, 0.7fr, 0.8fr, 0.8fr, 1.5fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Amendment Category (OBO Crosswalk)*], [*Scored Arms*], [*Improved*], [*Reduced*], [*Improvement Rate (95% Wilson CI)*],
    ..data.amendment_outcomes.map(r => (
      r.category,
      str(r.n_arms),
      str(r.n_improved),
      str(r.n_reduced),
      str(r.improved_pct) + "% (" + str(r.ci_low) + "–" + str(r.ci_high) + "%)",
    )).flatten()
  ),
  caption: [Empirical treatment-arm growth improvement rates relative to unamended regolith controls across standardized amendment categories, with 95% Wilson score confidence intervals.],
)

To test whether protocol metadata alone can predict treatment success without leaking report-level covariates across multi-arm experiments, we benchmarked four classifiers under 5-fold `StratifiedGroupKFold` cross-validation grouped on `report_id` (`#data.ml.n_train_arms` training arms; `#data.ml.n_test_arms` held-out test arms from disjoint reports; Table 5). The *Random Forest* classifier achieved the strongest out-of-fold discrimination with a CV ROC-AUC of `#data.ml.models.at(2).cv_roc_auc` (95% bootstrap CI: `#data.ml.models.at(2).cv_roc_auc_ci.at(0)`–`#data.ml.models.at(2).cv_roc_auc_ci.at(1)`) and CV PR-AUC of `#data.ml.models.at(2).cv_pr_auc` (`#data.ml.models.at(2).cv_pr_auc_ci.at(0)`–`#data.ml.models.at(2).cv_pr_auc_ci.at(1)`), followed by *HistGradientBoosting* (`CV ROC-AUC = #data.ml.models.at(3).cv_roc_auc`; `Test ROC-AUC = #data.ml.models.at(3).test_roc_auc`), both substantially outperforming the majority-class `Dummy` baseline (`CV ROC-AUC = 0.500`). Slice evaluation on the held-out report test set confirmed high predictive accuracy across both lunar (`91.7%` accuracy, `n = 12` arms) and Martian (`80.0%` accuracy, `n = 10` arms) test slices, as well as Main (`85.0%`, `n = 20`) and Junior (`100.0%`, `n = 4`) tracks.

#figure(
  table(
    columns: (1.8fr, 1.3fr, 1.3fr, 0.7fr, 0.9fr, 0.7fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Model (Grouped by `report_id`)*], [*CV ROC-AUC (95% CI)*], [*CV PR-AUC (95% CI)*], [*CV F1*], [*Test ROC-AUC*], [*Test F1*],
    ..data.ml.models.map(m => (
      m.model,
      str(m.cv_roc_auc) + " (" + str(m.cv_roc_auc_ci.at(0)) + "–" + str(m.cv_roc_auc_ci.at(1)) + ")",
      str(m.cv_pr_auc) + " (" + str(m.cv_pr_auc_ci.at(0)) + "–" + str(m.cv_pr_auc_ci.at(1)) + ")",
      str(m.cv_f1),
      if m.test_roc_auc == none { "N/A" } else { str(m.test_roc_auc) },
      str(m.test_f1),
    )).flatten()
  ),
  caption: [Leak-free supervised classification benchmark predicting positive growth response (`target_improved = 1`) under 5-fold `StratifiedGroupKFold` (`n = 104` training arms) and held-out `GroupShuffleSplit` (`n = 24` test arms).],
)

Global SHAP (`TreeExplainer`) feature attribution on the fitted Random Forest model (Figure 3B) revealed that `amendment_category` (specifically microbial/mycorrhizal inoculation vs. unbuffered mineral/nano additions), experimental rigor indicators (`has_unamended_regolith_control`, `experimental_duration_days`, `missing_duration`), crop guild (`root` and `leafy_green`), and competition year are the primary drivers of predicted growth improvement.

#if data.figures_present.fig3 [
  #figure(
    image("/manuscript/figures/fig3.png", width: 98%),
    caption: [(A) Empirical amendment improvement rates with 95% Wilson confidence intervals across scored treatment arms. (B) Top 10 global feature attributions (`mean |SHAP value|`) from the report-grouped Random Forest model.],
  )
]

== Regolith Bottlenecks, Sparsity Gaps, and Spring 2026 Exemplar Innovations

Text mining of physiological and physical failure modes across all `#data.total_pdf_reports` PDF reports (Table 6; Figure 4A) confirmed that *macronutrient deficiency* (`69.0%` of reports) and *environmental light/temperature sensitivity* (`65.8%`) are the most frequently documented operational constraints, followed closely by *physical substrate compaction and surface crusting* (`42.2%`), *hydrophobicity and poor water retention* (`35.8%`), *ionic/heavy-metal or perchlorate-analog salinity stress* (`26.7%`), *fungal/mold contamination* in organic-amended pots (`23.5%`), *alkaline pH lockup* (`21.9%`), and *mechanical root restriction* (`19.8%`).

#figure(
  table(
    columns: (2.6fr, 0.9fr, 1.0fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Extracted Regolith Stress / Failure Bottleneck*], [*PDF Reports*], [*Corpus Prevalence*],
    ..data.top_bottlenecks.map(b => (b.bottleneck, str(b.count), str(b.pct) + "%")).flatten()
  ),
  caption: [Prevalence of primary abiotic and biotic regolith bottlenecks identified across `187` Plant the Moon Challenge PDF reports.],
)

Cross-tabulating `Crop Guild × Amendment Category` across all `#data.total_treatment_arms` treatment arms (Figure 4B) exposed substantial experimental sparsity. While `leafy_green`, `legume`, and `root` guilds have been densely screened against organic compost, microbial inoculants, and coir/peat mixtures, critical combinations remain almost completely untested (`0–1` trial arms)—including *hydrogel/alginate encapsulation in legumes and grains*, *biochar carbon stabilization in fruiting and fungal systems*, and *microbial necromass or mycoponic co-culture across grain crops*.

#if data.figures_present.fig4 [
  #figure(
    image("/manuscript/figures/fig4.png", width: 98%),
    caption: [(A) Corpus-wide prevalence of cited regolith growth bottlenecks. (B) `Crop Guild × Amendment Category` trial-arm coverage matrix revealing high-priority experimental whitespace.],
  )
]

Crucially, the most recent `Spring 2026` Best in Show cohort illustrates a clear maturation toward mechanistic, closed-loop ISRU biotechnology (Table 7):
- *Sterilized Microbial Necromass Cycling (`Team Shonik`, High School):* Demonstrated that incorporating 15% w/w heat-inactivated or ethanol-inactivated microbial necromass into `LHS-1` lunar regolith simulant increased 20-day *Raphanus sativus* mean shoot height by `>120%` (`14.2 cm` heat-killed and `14.1 cm` ethanol-killed vs. `6.3 cm` in unamended regolith control) and fresh biomass nearly fivefold (`1.03 g` vs. `0.21 g`), proving that planetary-protection-compliant sterilized bioreactor waste can jump-start regolith fertility.
- *Alginate Spherification Media (`MCST Biotech 1`, High School):* Engineered sodium alginate hydrogel seed encapsulation spheres to overcome loose lunar regolith hydrophobicity and fine-dust compaction without requiring bulk terrestrial soil import.
- *Aquaculture Effluent + Hydrogel Synergy (`Smells fishy1!`, High School):* Combined simulated lunar regolith with closed-loop aquaculture waste and hydrogel polymers to sustain baby spinach (*Spinacia oleracea*), simultaneously addressing nitrogen/phosphorus scarcity and root-zone desiccation.
- *Mycoponic Regolith Biomanufacturing (`The Marshroomers`, Professional):* Cultivated *Pleurotus ostreatus* mycelium in Martian regolith simulant (`MGS-1`) for dual-purpose edible biomass production and regolith brick biocementation.
- *Nanoscale Food-Waste Valorization & Desert Microbiomes (`EPCC Team Artemis` & `Team Voyager`, Professional):* Evaluated banana-peel nano-fertilizers across factorial tomato/basil regolith trials (`n = 28` plants) and Chihuahuan Desert extremophile soil microbial consortia for early *Lactuca sativa* establishment in lunar regolith.

#figure(
  table(
    columns: (1.1fr, 1.0fr, 0.7fr, 0.8fr, 2.5fr, 0.8fr),
    inset: 4.5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Team Name*], [*Division*], [*Target*], [*Focal Crop*], [*Project Title & Experimental Focus*], [*SHA-256*],
    ..data.exemplar_studies.map(e => (
      e.team,
      e.division,
      e.target,
      e.crop,
      e.title,
      raw(e.sha256_prefix),
    )).flatten()
  ),
  caption: [Exemplar `Spring 2026` Main-track Best in Show studies illustrating closed-loop ISRU amendments, microbial consortia, and biopolymer encapsulation, linked to verified PDF SHA-256 prefixes.],
)

= Discussion

== Mechanistic Synergy: Coupling Biogeochemical Nutrient Release with Hydraulic Matrix Engineering

Synthesizing `#data.total_arms` trial arms across twelve seasons of the Plant the Moon Challenge reveals a unifying mechanistic principle for extraterrestrial regolith agriculture: *neither chemical fertilization nor physical substrate conditioning is sufficient in isolation*. Unamended lunar (`LHS-1`, `LMS-1`) and Martian (`MGS-1`, `MMS-1`) simulants confront plant roots with coupled, compounding stressors @paul2022plants @longfox2023geomechanical @cannon2019mars. Fine, sharp glass and plagioclase particles pack into high-bulk-density matrices upon watering, collapsing macropore oxygen diffusion and creating a hydrophobic or crusted surface barrier (`42.2%` and `35.8%` corpus prevalence, respectively). When teams apply concentrated synthetic NPK salts directly to unbuffered 100% regolith, high baseline alkalinity (`pH 8.5–10.0`, cited in `21.9%` of reports) and low cation exchange capacity (CEC) induce osmotic shock or micronutrient precipitation—explaining why unbuffered mineral/nano additions exhibit lower reliability (`60.0%` improvement rate) than biologically complex amendments.

In contrast, interventions that introduce *amphiphilic organic polymers and active or inactivated microbial matrices*—such as vermicompost/aquaculture effluents (`100.0%`), mycorrhizal/bacterial inoculants (`92.0%`), compost (`80.0%`), and coir/alginate hydrogels (`77.3%`)—simultaneously buffer rhizosphere pH, form organo-mineral micro-aggregates that prevent mechanical crusting, increase water-holding capacity, and chelate iron/phosphate ions into bioavailable forms. The `Spring 2026` microbial necromass findings of *Team Shonik* provide a particularly important blueprint for planetary protection: even when live microbial inoculants are restricted by forward-contamination rules, thermally sterilized microbial necromass retains amino-sugar cell-wall polymers and slow-release organic nitrogen capable of increasing radish biomass fivefold in lunar regolith.

== Closing the Citizen-Science Experimental Rigor Gap

From a meta-scientific and educational standpoint, our division-level audit (Table 2) highlights both the triumph and the primary vulnerability of student citizen-science archives. While `#data.earth_ctrl_pct%` of teams include an Earth potting-soil control, only `#data.reg_ctrl_pct%` include a `100% unamended regolith` negative control. Comparing an amended regolith mixture (e.g., 75% `LHS-1` + 25% compost) solely against 100% Miracle-Gro potting soil confounds two distinct questions: (a) how well regolith performs relative to optimal terrestrial media, and (b) whether the specific amendment improved plant performance _over unamended regolith_. Always requiring a three-tier control architecture—(1) _Terrestrial Positive Control_, (2) _100% Unamended Regolith Negative Control_, and (3) _Graded Treatment Arms_—together with basic dispersion metrics (mean, standard deviation, replicate count $n$, and ANOVA or _t_-test $p$-values, currently reported in only `#data.stat_test_pct%` of PDFs) would dramatically increase the statistical power of future PTMC cohorts for formal random-effects meta-regression (Hedges' $g$ and log response ratio $ln(macron(X)_"trt" / macron(X)_"ctrl")$).

== Limitations and Future Integration with NASA Lunar LEAF & CoSE Digital Twins

Two methodological limitations should be noted when interpreting this baseline release. First, while our deterministic v2 table-aware heuristic extractor achieves `100%` verbatim quote provenance verification and `92.5%` taxonomic coverage across all `187` PDFs with zero external API keys, student teams format quantitative measurements across highly varied Word tables, embedded spreadsheet screenshots, and narrative paragraphs. Consequently, continuous numeric endpoints (`germination_rate_pct`, `mean_shoot_height_cm`, `mean_fresh_biomass_g`) remain sparse under heuristic parsing alone. The `ptm-meta` package includes a production-ready multimodal *Gemini Structured Outputs* backend (`ptm-meta extract --backend gemini`) that ingests native PDF byte streams and all `1,206` extracted tables to populate dense numeric effect sizes across both digital and scanned reports whenever an API key is supplied. Second, because the public archive indexes award-winning reports, positive publication bias (`82.8%` positive treatment arms) is expected relative to all classroom entrants.

Looking forward, the FAIR datasets, OBO ontology mappings, and sparsity matrix generated here feed directly into the *Collaborative Science Environment (CoSE)* and NASA *Lunar LEAF* (Lunar Effects on Agricultural Flora) research ecosystem @barker2020toast @scott2024nasa. By linking citizen-science regolith screening data with spaceflight transcriptomic baselines in NASA OSDR and TOAST, student cohorts worldwide can prioritize the exact `Crop Guild × Simulant × Amendment` gaps identified in Figure 4B.

= Data and Code Availability

In accordance with the FAIR Guiding Principles @wilkinson2016fair, the complete source code (`ptm-meta` Python package), locked `uv` dependency manifest (`pyproject.toml`, `uv.lock`), SHA-256 PDF provenance manifest (`data/raw/manifest.csv`), Draft 2020-12 JSON Schemas (`schemas/`), OBO ontology crosswalks (`data/processed/ontology_mappings.json`), normalized analysis datasets (`reports.{csv,parquet,json}` and `trial_arms.{csv,parquet,json}`), executable Jupyter notebooks (`book/notebooks/01`–`04`), Typst manuscript source (`manuscript/ptm_manuscript.typ` and `manuscript/references.bib`), and RO-Crate 1.1 metadata (`ro-crate-metadata.json`) @soilandreyes2022packaging are permanently available under MIT / CC-BY-4.0 licenses at `https://github.com/dr-richard-barker/Plant_the_moon` and interactively hosted via GitHub Pages at `https://dr-richard-barker.github.io/Plant_the_moon/`.

#bibliography("/manuscript/references.bib", title: "References", style: "nature")
