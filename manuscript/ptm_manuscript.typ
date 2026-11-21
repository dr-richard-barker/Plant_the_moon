#let data = json("/manuscript/manuscript_data.json")

#set document(
  title: "FAIR AI/ML Meta-Analysis of Plant the Moon Challenge Regolith Reports (2021–2026)",
  author: "Richard J. Barker",
)

#set page(
  paper: "us-letter",
  margin: (x: 0.72in, y: 0.75in),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: rgb("#5f7f8a"))
      #grid(
        columns: (1fr, auto),
        [CoSE Meta-Analysis · Plant the Moon Challenge (2021–2026)],
        [Page #counter(page).display()],
      )
      #line(length: 100%, stroke: 0.5pt + rgb("#cfdde1"))
    ]
  },
)

#set text(font: ("IBM Plex Sans", "Helvetica Neue", "Arial"), size: 9.8pt, fill: rgb("#0f2a33"))
#set par(justify: true, leading: 0.58em)
#set heading(numbering: "1.1")

#show heading: it => {
  set text(fill: rgb("#004053"), weight: "semibold")
  v(0.55em)
  it
  v(0.2em)
}

// Title Header Banner (CoSE Accent)
#box(
  width: 100%,
  fill: rgb("#eaf1f3"),
  stroke: (left: 4pt + rgb("#004053")),
  inset: 14pt,
  radius: 4pt,
)[
  #text(size: 8.2pt, fill: rgb("#0f7f9f"), weight: "bold")[COLLABORATIVE SCIENCE ENVIRONMENT (CoSE) · FAIR SYNTHESIS MANUSCRIPT]
  #v(0.35em)
  #text(size: 16pt, weight: "bold", fill: rgb("#004053"))[
    FAIR AI/ML Meta-Analysis of Student Regolith Plant-Growth Research Across the Plant the Moon Challenge (2021–2026)
  ]
  #v(0.4em)
  #text(size: 9.5pt, fill: rgb("#3d5a64"))[
    *Richard J. Barker, PhD* · Collaborative Science Environment (CoSE) · ORCID: 0000-0001-5681-9857 \
    Repository: `github.com/dr-richard-barker/Plant_the_moon` · License: MIT / CC-BY-4.0
  ]
]

#v(0.7em)

// Abstract Box
#box(
  width: 100%,
  stroke: 0.75pt + rgb("#cfdde1"),
  inset: 11pt,
  radius: 4pt,
)[
  *Abstract.* Sustaining crops in extraterrestrial lunar and Martian regolith is a central challenge for bioregenerative life support systems (BLSS). Over twelve competition seasons (`Spring 2021`–`Spring 2026`), student teams participating in the *Plant the Moon Challenge* have generated hundreds of experimental studies testing regolith simulants, soil amendments, microbial inoculants, and hydroponic/encapsulation strategies. Here we present an open, FAIR-compliant (Findable, Accessible, Interoperable, Reusable) computational pipeline that ingests all `24` archived awards pages (`#data.total_award_entries` award entries; `#data.total_pdf_reports` full-text PDF reports spanning `#data.total_pages` pages and `#data.total_tables` extracted tables), maps biological taxa and amendments to OBO Foundry ontologies (`NCBITaxon`, `ENVO`, `AGRO`), extracts `#data.total_arms` structured experimental arms with verbatim page-cited provenance, and evaluates grouped machine-learning models (`StratifiedGroupKFold` by `report_id`) to synthesize which interventions reliably improve plant performance over unamended regolith.
]

#v(0.6em)

// KPI Strip
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 8pt,
  ..(("PDF Reports", str(data.total_pdf_reports)),
     ("Pages / Tables", str(data.total_pages) + " / " + str(data.total_tables)),
     ("Trial Arms", str(data.total_arms)),
     ("NCBITaxon Mapped", str(data.ncbitaxon_mapped))).map(((lbl, val)) => box(
    width: 100%, fill: rgb("#f5f8f9"), stroke: 0.6pt + rgb("#cfdde1"), inset: 8pt, radius: 4pt,
  )[
    #text(size: 13pt, weight: "bold", fill: rgb("#004053"))[#val] \
    #text(size: 7.8pt, fill: rgb("#5f7f8a"))[#lbl]
  ])
)

= Introduction

Long-duration lunar and Martian surface missions require in-situ resource utilization (ISRU) coupled with plant-based bioregenerative life support. Terrestrial experiments using lunar highlands (`LHS-1`), lunar mare (`LMS-1`), and Martian (`MGS-1`, `MMS-1`) regolith simulants consistently face severe abiotic constraints: absence of organic carbon and nitrogen cycling, alkaline pH (often pH 8.5–10.2 in lunar simulants), surface crusting, poor water-holding capacity, and low nutrient bioavailability.

The *Plant the Moon Challenge* (organized by the Institute of Competition Sciences) provides a unique multi-year citizen-science and academic experimental corpus spanning Elementary, Middle, High School, and Professional/University cohorts. However, these findings remain locked in heterogeneous PDF lab reports, posters, and slide decks. We built a reproducible FAIR ingestion, extraction, and ML meta-analysis workflow to unify this corpus into machine-actionable datasets and an interactive CoSE GitHub Pages portal.

= FAIR Ingestion & Hybrid Extraction Architecture

All `24` archived awards pages (`Spring 2021`–`Spring 2026`, Main and Junior `/jr/` tracks) were scraped with deterministic `report_id` hashing, deduplicated across overlapping Best in Show, State Award, and Space Grant tiers, and verified via SHA-256 digests (`187/187` PDFs). Text and tables were extracted using `PyMuPDF` and `pdfplumber` (`185` digital-text PDFs and `2` image/scanned PDFs).

Structured scientific records (`schemas/experiment_record.schema.json`) were extracted with mandatory verbatim `evidence_quote` and `page_number` provenance, mapped to `NCBITaxon` and `ENVO`/`AGRO`/`PECO` URIs (`data/processed/ontology_mappings.json`), and packaged into an RO-Crate 1.1 bundle (`ro-crate-metadata.json`).

= Corpus Scientometrics & Experimental Rigor

Across `#data.total_pdf_reports` analyzed PDFs, `#data.celestial_counts.at("lunar", default: 0)` focus primarily on lunar regolith, `#data.celestial_counts.at("martian", default: 0)` on Martian regolith, and `#data.celestial_counts.at("both", default: 0)` compare both simulants. Regarding experimental rigor, `#data.earth_ctrl_pct%` include a terrestrial/potting soil positive control, `#data.reg_ctrl_pct%` include an unamended 100% regolith negative control, and `#data.stat_test_pct%` report formal statistical hypothesis tests (e.g., ANOVA, *t*-tests, Tukey HSD).

#if data.figures_present.fig1 [
  #figure(
    image("/manuscript/figures/fig1.png", width: 96%),
    caption: [Archive distribution, experimental control adoption, and missingness audit across 12 Plant the Moon Challenge seasons (2021–2026).],
  )
]

= Unsupervised Protocol Archetypes & Amendment Outcomes

TF-IDF + SVD semantic embeddings combined with protocol encodings cluster student experiments into reproducible research themes (e.g., microbial/mycorrhizal bio-inoculants, hydrogel/alginate water-retention matrices, organic/aquaculture waste valorization, and synthetic/mineral nutrient trials). Table 1 summarizes observed outcome rates across scored treatment arms.

#table(
  columns: (2.2fr, 0.7fr, 0.8fr, 1.3fr),
  inset: 5pt,
  stroke: 0.4pt + rgb("#cfdde1"),
  fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
  [*Amendment Category*], [*Arms*], [*Improved*], [*Rate (95% Wilson CI)*],
  ..data.amendment_outcomes.map(r => (
    r.category,
    str(r.n_arms),
    str(r.n_improved),
    str(r.improved_pct) + "% (" + str(r.ci_low) + "–" + str(r.ci_high) + "%)",
  )).flatten()
)

#if data.figures_present.fig2 [
  #figure(
    image("/manuscript/figures/fig2.png", width: 94%),
    caption: [2D UMAP/PCA projection of extracted experimental protocols colored by unsupervised cluster archetype.],
  )
]

= Leak-Free Predictive ML & Meta-Regression

To prevent data leakage across multiple treatment arms belonging to the same student report, all train/test splits and 5-fold cross-validation (`StratifiedGroupKFold`) were strictly grouped by `report_id`, with imputation, one-hot encoding, and scaling fit exclusively inside training folds.

#if data.ml.len() > 0 [
  Across `#data.ml.n_total_arms` scored treatment arms (`#data.ml.n_unique_reports` unique reports), Table 2 compares model performance against a majority-class baseline (`best model`: *#data.ml.best_model*).

  #table(
    columns: (1.8fr, 1.2fr, 1.2fr, 0.8fr, 0.9fr),
    inset: 5pt,
    stroke: 0.4pt + rgb("#cfdde1"),
    fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
    [*Model*], [*CV ROC-AUC (95% CI)*], [*CV PR-AUC (95% CI)*], [*CV F1*], [*Test ROC-AUC*],
    ..data.ml.models.map(m => (
      m.model,
      str(m.cv_roc_auc) + " (" + str(m.cv_roc_auc_ci.at(0)) + "–" + str(m.cv_roc_auc_ci.at(1)) + ")",
      str(m.cv_pr_auc) + " (" + str(m.cv_pr_auc_ci.at(0)) + "–" + str(m.cv_pr_auc_ci.at(1)) + ")",
      str(m.cv_f1),
      if m.test_roc_auc == none { "N/A" } else { str(m.test_roc_auc) },
    )).flatten()
  )
]

#if data.figures_present.fig3 [
  #figure(
    image("/manuscript/figures/fig3.png", width: 96%),
    caption: [Amendment effect synthesis with 95% confidence intervals and SHAP feature attributions for predicting positive regolith growth response.],
  )
]

= Regolith Bottlenecks, Research Gaps & Lunar LEAF Relevance

Extracted bottleneck frequencies highlight nutrient deficiency, hydrophobicity/water retention, alkaline pH stress, and surface compaction/crusting as the most commonly cited physiological barriers.

#table(
  columns: (2.5fr, 0.8fr, 0.9fr),
  inset: 5pt,
  stroke: 0.4pt + rgb("#cfdde1"),
  fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
  [*Reported Bottleneck*], [*Reports*], [*Prevalence*],
  ..data.top_bottlenecks.map(b => (b.bottleneck, str(b.count), str(b.pct) + "%")).flatten()
)

#if data.figures_present.fig4 [
  #figure(
    image("/manuscript/figures/fig4.png", width: 96%),
    caption: [Crop guild × amendment sparsity matrix highlighting under-tested combinations and regolith bottleneck frequency.],
  )
]

= Data Availability & FAIR Provenance

All source code, JSON Schemas, SHA-256 PDF manifests, `CITATION.cff`, `codemeta.json`, `ro-crate-metadata.json`, and interactive Jupyter Book notebooks are openly published at `https://github.com/dr-richard-barker/Plant_the_moon` and rendered via GitHub Pages at `https://dr-richard-barker.github.io/Plant_the_moon/`.
