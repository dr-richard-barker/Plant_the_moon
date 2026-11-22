#let data = json("/manuscript/manuscript_data.json")

#set document(
  title: "Multi-Stakeholder Presentation: FAIR AI/ML Meta-Analysis of the Plant the Moon Challenge (2021–2026)",
  author: "Richard J. Barker",
)

#set page(
  paper: "presentation-16-9",
  margin: (x: 0.44in, y: 0.34in),
  fill: rgb("#f5f8f9"),
  footer: context [
    #set text(size: 8.5pt, fill: rgb("#5f7f8a"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cfdde1"))
    #v(2pt)
    #grid(
      columns: (1fr, auto),
      [CoSE · Plant the Moon Challenge FAIR Meta-Analysis (2021–2026) · `dr-richard-barker.github.io/Plant_the_moon`],
      [Slide #counter(page).display("1 / 1", both: true)],
    )
  ],
)

#set text(font: ("Helvetica Neue", "Arial"), size: 11.2pt, fill: rgb("#0f2a33"))
#set par(justify: false, leading: 0.46em)

#let slide_header(stage_tag, stage_color, title_txt, subtitle_txt) = [
  #box(
    width: 100%,
    fill: rgb("#ffffff"),
    stroke: (left: 5pt + stage_color, rest: 0.6pt + rgb("#cfdde1")),
    inset: (x: 11pt, y: 7pt),
    radius: 5pt,
  )[
    #text(size: 8.8pt, weight: "bold", fill: stage_color)[#stage_tag] \
    #v(1pt)
    #text(size: 16.5pt, weight: "bold", fill: rgb("#004053"))[#title_txt] \
    #text(size: 10pt, fill: rgb("#3d5a64"))[#subtitle_txt]
  ]
  #v(4pt)
]

#let takeaway_box(stage_color, txt) = [
  #v(1fr)
  #box(
    width: 100%,
    fill: rgb("#eaf1f3"),
    stroke: (left: 4pt + stage_color),
    inset: 7pt,
    radius: 4pt,
  )[
    #text(size: 10pt, fill: rgb("#0f2a33"))[*Stakeholder Takeaway:* #txt]
  ]
]

// =========================================================================
// SLIDE 1: Title & Multi-Stage Roadmap
// =========================================================================
#box(
  width: 100%,
  fill: rgb("#004053"),
  inset: 22pt,
  radius: 8pt,
)[
  #text(size: 11pt, weight: "bold", fill: rgb("#7ec3d8"))[COLLABORATIVE SCIENCE ENVIRONMENT (CoSE) · MULTI-STAKEHOLDER BRIEFING]
  #v(6pt)
  #text(size: 26pt, weight: "bold", fill: rgb("#ffffff"))[
    FAIR AI/ML Meta-Analysis of Student Regolith Plant-Growth Research (2021–2026)
  ]
  #v(6pt)
  #text(size: 13.5pt, fill: rgb("#d7ebf1"))[
    Synthesizing 12 Seasons of the Plant the Moon Challenge Across Four Stakeholder Stages
  ]
  #v(10pt)
  #text(size: 11pt, fill: rgb("#b5c9cf"))[
    *Richard J. Barker, PhD* · CoSE Benefit Corp · NASA OSDR Plant AWG Chair · NASA Lunar LEAF Science Co-Lead \
    ORCID: `0000-0001-5681-9857` · Live Portal: `https://dr-richard-barker.github.io/Plant_the_moon/`
  ]
]

#v(10pt)

#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 10pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#004053"), rest: 0.6pt + rgb("#cfdde1")), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#004053"))[STAGE 1 · SLIDES 3–5] \
    #text(size: 13pt, weight: "bold")[Program Leadership & Sponsors] \
    #text(size: 10.5pt, fill: rgb("#3d5a64"))[ICS, NASA Space Grant Consortia & Funders: 12-season scale, rigor audit & 3-tier control rubric policy.]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#3f7d4e"), rest: 0.6pt + rgb("#cfdde1")), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#3f7d4e"))[STAGE 2 · SLIDES 6–8] \
    #text(size: 13pt, weight: "bold")[Educators & Student Teams] \
    #text(size: 10.5pt, fill: rgb("#3d5a64"))[K–12 & University Coaches: winning crop guilds, top amendments, failure traps & untried project matrix.]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#0f7f9f"), rest: 0.6pt + rgb("#cfdde1")), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#0f7f9f"))[STAGE 3 · SLIDES 9–11] \
    #text(size: 13pt, weight: "bold")[Space Biology & Lunar LEAF] \
    #text(size: 10.5pt, fill: rgb("#3d5a64"))[BLSS Scientists: coupled nutrient/hydraulic synergy, sterilized necromass, mycoponics & Apollo baselines.]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#d97706"), rest: 0.6pt + rgb("#cfdde1")), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#d97706"))[STAGE 4 · SLIDES 12–14] \
    #text(size: 13pt, weight: "bold")[AI/ML & FAIR Engineers] \
    #text(size: 10.5pt, fill: rgb("#3d5a64"))[Open-Science Developers: SHA-256 provenance, OBO ontologies, RO-Crate 1.1 & leak-free grouped ML.]
  ],
)

#pagebreak()

// =========================================================================
// SLIDE 2: Overview · Corpus at a Glance
// =========================================================================
#slide_header(
  "OVERVIEW · SHARED EVIDENCE BASE",
  rgb("#004053"),
  "Twelve Competition Seasons Unified into One FAIR Knowledge Base",
  "Complete scrape, SHA-256 verification, and structured extraction across Spring 2021 – Spring 2026",
)

#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 10pt,
  ..(("24 Pages / 12 Seasons", str(data.total_award_entries) + " Award Entries", "Main (HS/Pro) + Junior (Elem/MS)"),
     (str(data.total_pdf_reports) + " Verified PDFs", str(data.total_pages) + " Pages Parsed", str(data.total_tables) + " Structured Tables Extracted"),
     (str(data.total_arms) + " Trial Arms", str(data.total_treatment_arms) + " Treatment Arms", "205 Earth & Regolith Control Arms"),
     (str(data.ncbitaxon_mapped) + " Taxa Mapped", str(data.ncbitaxon_pct) + "% NCBITaxon", "Crosswalked to ENVO, AGRO, CHEBI, PECO")).map(((top_l, big_v, sub_l)) => box(
    width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt,
  )[
    #text(size: 9.5pt, weight: "bold", fill: rgb("#0f7f9f"))[#top_l] \
    #v(2pt)
    #text(size: 18pt, weight: "bold", fill: rgb("#004053"))[#big_v] \
    #v(2pt)
    #text(size: 9.5pt, fill: rgb("#5f7f8a"))[#sub_l]
  ])
)

#v(8pt)
#grid(
  columns: (1.1fr, 1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 12pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#004053"))[Why Synthesize Student Regolith Reports?]
    #list(
      [*Parallelized combinatorial screening:* Thousands of students test novel organic, microbial, and polymeric amendments across lunar (`70.6%`) and Martian (`25.1%`) simulants.],
      [*Previously locked in unstructured PDFs:* Heterogeneous lab reports, posters, and slide decks lacked unified metadata or cross-season meta-analysis.],
      [*Now 100% FAIR:* Every record is linked to its SHA-256-verified source PDF, OBO Foundry ontology URI, and verbatim page-cited quote.],
    )
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 12pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#004053"))[Celestial Target Breakdown (`n = 187` PDFs)]
    #v(4pt)
    #table(
      columns: (1.4fr, 0.8fr, 0.8fr),
      inset: 5pt,
      stroke: 0.4pt + rgb("#cfdde1"),
      fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
      [*Target Environment*], [*PDF Reports*], [*Share*],
      [Lunar Regolith (`LHS-1`, `LMS-1`)], [#str(data.celestial_counts.at("lunar", default: 0))], [70.6%],
      [Martian Regolith (`MGS-1`, `MMS-1`)], [#str(data.celestial_counts.at("martian", default: 0))], [25.1%],
      [Dual Lunar + Martian Comparison], [#str(data.celestial_counts.at("both", default: 0))], [3.2%],
      [Unspecified / Scanned Image PDF], [#str(data.celestial_counts.at("unspecified", default: 0))], [1.1%],
    )
  ],
)

#takeaway_box(rgb("#004053"), [The Plant the Moon Challenge represents the largest open educational experimental corpus in astrobotany (`187` full-text reports, `581` arms), now accessible for quantitative synthesis.])

#pagebreak()

// =========================================================================
// SLIDE 3: Stage 1 · Program Leadership & Sponsors (Archive Scale)
// =========================================================================
#slide_header(
  "STAGE 1 · PROGRAM LEADERSHIP, ICS & NASA SPACE GRANT SPONSORS",
  rgb("#004053"),
  "Sustained Multi-Division Participation & Longitudinal Rigor (2021–2026)",
  "Tracking 12 seasons of Best in Show, State Award, and NASA Space Grant Regional Expansion cohorts",
)

#grid(
  columns: (1.35fr, 1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 8pt, radius: 6pt)[
    #if data.figures_present.fig1 [
      #image("/manuscript/figures/fig1.png", width: 100%)
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#004053"))[Key Program Findings for Sponsors]
    #list(
      [*Consistent national throughput:* `15–18` Best in Show PDF reports published every season since Fall 2021 across Elementary, Middle, High School, and University tracks.],
      [*Space Grant amplification:* Regional expansion awards in `FL`, `GA`, `IA`, `MA`, `MI`, `MO`, `NC`, `PR`, `SC`, `TX`, `VA`, `WV`, and `CA` broaden participation beyond traditional aerospace hubs.],
      [*High positive-control adoption (`71.7%`):* Students reliably include Earth potting soil, but unamended 100% regolith negative controls (`38.0%`) lag behind.],
    )
  ],
)

#takeaway_box(rgb("#004053"), [Program scale is thriving across all four educational divisions; the single highest-leverage opportunity for sponsors is standardizing control-group reporting.])

#pagebreak()

// =========================================================================
// SLIDE 4: Stage 1 · Division-Level Experimental Rigor Audit
// =========================================================================
#slide_header(
  "STAGE 1 · PROGRAM LEADERSHIP, ICS & NASA SPACE GRANT SPONSORS",
  rgb("#004053"),
  "Benchmarking Experimental Rigor Across Educational Divisions",
  "Document depth, tabular data density, control architectures, and inferential statistics by age division",
)

#table(
  columns: (1.8fr, 0.8fr, 0.9fr, 0.9fr, 1.1fr, 1.2fr, 1.1fr),
  inset: 7pt,
  stroke: 0.45pt + rgb("#cfdde1"),
  fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { rgb("#ffffff") },
  [*Competition Division*], [*PDFs*], [*Mean Pages*], [*Mean Tables*], [*Earth Soil Control*], [*100% Regolith Control*], [*Statistical Test*],
  ..data.division_rigor.map(d => (
    d.division,
    str(d.n_pdfs),
    str(d.mean_pages),
    str(d.mean_tables),
    str(d.earth_ctrl_pct) + "%",
    str(d.reg_ctrl_pct) + "%",
    str(d.stat_test_pct) + "%",
  )).flatten()
)

#v(8pt)
#grid(
  columns: (1fr, 1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 11.5pt, weight: "bold", fill: rgb("#004053"))[What Works Well]
    #list(
      [*High School & Professional depth:* Average `15.7–18.3` pages and `6.9–8.4` data tables per report.],
      [*Strong Earth baseline adoption:* `66.7–77.8%` of teams include an Earth potting soil control arm.],
    )
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 11.5pt, weight: "bold", fill: rgb("#be123c"))[The Meta-Analysis Bottleneck]
    #list(
      [*Missing 100% regolith baseline (`38.0%`):* Without an unamended regolith negative control, amendment uplift cannot be decoupled from baseline simulant fertility.],
      [*Low statistical reporting (`15.0%`):* Few teams report SD/SE or ANOVA/$t$-tests.],
    )
  ],
)

#takeaway_box(rgb("#004053"), [Progression from Elementary (`10.1` pp., `2.2%` stats) to Professional (`18.3` pp., `29.6%` stats) demonstrates strong STEM scaffolding across the PTMC pipeline.])

#pagebreak()

// =========================================================================
// SLIDE 5: Stage 1 · Policy Proposal: The 3-Tier FAIR Rubric
// =========================================================================
#slide_header(
  "STAGE 1 · PROGRAM LEADERSHIP, ICS & NASA SPACE GRANT SPONSORS",
  rgb("#004053"),
  "Actionable Policy: A 3-Tier Control & Tabular Submission Rubric",
  "How a minor rubric update turns future student cohorts into a gold-standard NASA meta-analysis dataset",
)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 10pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#3f7d4e"), rest: 0.6pt + rgb("#cfdde1")), inset: 12pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#3f7d4e"))[PILLAR 1 · MANDATORY 3-TIER CONTROLS] \
    #v(4pt)
    Every team runs at least:
    + *Positive Control:* 100% Earth potting soil (`0%` regolith).
    + *Negative Control:* 100% unamended regolith simulant (`100%` regolith).
    + *Treatment Arms:* Graded amendment or microbial interventions (`n >= 3` replicate pots/arm).
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#0f7f9f"), rest: 0.6pt + rgb("#cfdde1")), inset: 12pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#0f7f9f"))[PILLAR 2 · STANDARDIZED SUMMARY TABLE] \
    #v(4pt)
    Require one mandatory structured table in every final PDF:
    - Simulant code (`LHS-1`, `LMS-1`, `MGS-1`)
    - Replicate pots ($n$) & seeds/pot
    - Germination `%`, final height (`cm ± SD`), fresh/dry biomass (`g ± SD`), and initial/final `pH`.
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#004053"), rest: 0.6pt + rgb("#cfdde1")), inset: 12pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#004053"))[PILLAR 3 · AUTOMATED FAIR INGESTION] \
    #v(4pt)
    Run `ptm-meta` at the close of each season (`Fall` & `Spring`):
    - Instant SHA-256 verification & `NCBITaxon`/`ENVO` tagging.
    - Publishes updated longitudinal benchmarks to the CoSE GitHub Pages portal.
  ],
)

#takeaway_box(rgb("#004053"), [Adopting the 3-Tier Control & Summary Table rubric will raise paired effect-size (`Hedges' g` / `LRR`) coverage from `<10%` to `>90%` in future cohorts.])

#pagebreak()

// =========================================================================
// SLIDE 6: Stage 2 · Educators, Coaches & Student Teams (Crop Selection)
// =========================================================================
#slide_header(
  "STAGE 2 · K–12 & UNIVERSITY EDUCATORS, COACHES & STUDENT TEAMS",
  rgb("#3f7d4e"),
  "Choosing Your Model Crop: Taxonomic Benchmarks Across 187 Reports",
  "Fast-cycling root crops, nitrogen-fixing legumes, and leafy greens dominate winning designs",
)

#grid(
  columns: (1.35fr, 1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 8pt, radius: 6pt)[
    #table(
      columns: (1.1fr, 1.4fr, 1.1fr, 1.0fr, 0.7fr),
      inset: 4.5pt,
      stroke: 0.4pt + rgb("#cfdde1"),
      fill: (_, row) => if row == 0 { rgb("#e1efe4") } else { none },
      [*Crop*], [*Scientific Name*], [*NCBITaxon*], [*Guild*], [*PDFs*],
      ..data.top_crops.slice(0, 8).map(c => (
        c.crop,
        emph(c.scientific),
        raw(c.ncbitaxon),
        c.guild,
        str(c.count) + " (" + str(c.pct) + "%)",
      )).flatten()
    )
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#3f7d4e"))[Coach & Student Selection Guide]
    #list(
      [*Best for 3–5 week windows:* Radish (_Raphanus sativus_, `18.2%`) and microgreens/cress germinate in 2–4 days and tolerate moderate alkalinity.],
      [*Best for microbial symbiosis:* Bush bean (_Phaseolus vulgaris_), pea (_Pisum sativum_), and mung bean pair naturally with _Rhizobium_ inoculants.],
      [*High-sensitivity bio-indicators:* Spinach (_S. oleracea_) and lettuce (_L. sativa_) clearly reveal chlorosis and water-retention differences.],
    )
  ],
)

#takeaway_box(rgb("#3f7d4e"), [Match crop maturation time to the 8-week PTMC window: fast vegetative/taproot crops provide quantitative biomass long before fruiting crops set seed.])

#pagebreak()

// =========================================================================
// SLIDE 7: Stage 2 · Educators & Students (What Amendments Win?)
// =========================================================================
#slide_header(
  "STAGE 2 · K–12 & UNIVERSITY EDUCATORS, COACHES & STUDENT TEAMS",
  rgb("#3f7d4e"),
  "What Actually Works in Regolith? Empirical Amendment Rankings",
  "Biological nutrient cycling + physical moisture matrices outperform raw chemical salts",
)

#grid(
  columns: (1.2fr, 1.1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 8pt, radius: 6pt)[
    #table(
      columns: (1.8fr, 0.6fr, 1.4fr),
      inset: 5pt,
      stroke: 0.4pt + rgb("#cfdde1"),
      fill: (_, row) => if row == 0 { rgb("#e1efe4") } else { none },
      [*Amendment Class*], [*Arms*], [*Improved (95% CI)*],
      ..data.amendment_outcomes.slice(0, 8).map(r => (
        r.category,
        str(r.n_arms),
        str(r.improved_pct) + "% (" + str(r.ci_low) + "–" + str(r.ci_high) + "%)",
      )).flatten()
    )
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#3f7d4e"))[3 Rules for Student Experimental Design]
    + *Buffer pH & porosity first:* Pure `LHS-1` / `MGS-1` compacts into concrete-like crusts when top-watered. Blend 15–30% organic matrix (coir, compost, vermicompost) or bottom-wick irrigate.
    + *Pair microbes with organic carbon:* Mycorrhizae and _Rhizobium_ (`92.0%` improved) thrive when paired with humic/compost substrates.
    + *Avoid over-salting:* Direct synthetic NPK or raw mineral salts without organic buffering frequently cause osmotic burn (`40%` neutral/reduced).
  ],
)

#takeaway_box(rgb("#3f7d4e"), [Winning teams solve *two* problems at once: slow-release biological nutrient delivery (vermicompost/microbes) + physical pore/moisture retention (coir/hydrogel).])

#pagebreak()

// =========================================================================
// SLIDE 8: Stage 2 · Educators & Students (Untried Project Finder)
// =========================================================================
#slide_header(
  "STAGE 2 · K–12 & UNIVERSITY EDUCATORS, COACHES & STUDENT TEAMS",
  rgb("#3f7d4e"),
  "Where Should Your Team Innovate Next? The Sparsity Opportunity Map",
  "Use the Crop Guild × Amendment coverage matrix to pick high-impact, under-tested experiments",
)

#grid(
  columns: (1.35fr, 1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 6pt, radius: 6pt)[
    #if data.figures_present.fig4 [
      #image("/manuscript/figures/fig4.png", width: 100%)
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#3f7d4e"))[Top 4 Open Innovation Opportunities]
    #list(
      [*1. Hydrogel / Alginate + Legumes or Grains (`0–1` arms):* Test sodium alginate seed encapsulation with nitrogen-fixing beans or wheat/rice.],
      [*2. Biochar + Fungal Mycoponics (`0` arms):* Pair biochar pH/ion adsorption with _Pleurotus_ mycelial regolith conditioning.],
      [*3. Sterilized Microbial Necromass Dose Curves:* Replicate *Team Shonik*'s heat-killed necromass across Martian `MGS-1` and leafy greens.],
      [*4. Capillary Wick vs. Drip Irrigation:* Quantify crusting reduction in 85–100% regolith.],
    )
  ],
)

#takeaway_box(rgb("#3f7d4e"), [Don't repeat basic potting-soil dilutions—target the `0` and `1` cells in Figure 4B with a rigorous 3-tier control setup to stand out for Best in Show.])

#pagebreak()

// =========================================================================
// SLIDE 9: Stage 3 · Space Biology, BLSS & NASA Lunar LEAF Scientists
// =========================================================================
#slide_header(
  "STAGE 3 · SPACE BIOLOGY, BLSS & NASA LUNAR LEAF RESEARCHERS",
  rgb("#0f7f9f"),
  "Mechanistic Synthesis: Coupled Abiotic Stressors in Extraterrestrial Regolith",
  "Bridging authentic Apollo lunar regolith transcriptomics with 187 macro-scale amendment trials",
)

#grid(
  columns: (1.1fr, 1.1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#0f7f9f"))[From Apollo Transcriptomics to Macro-Phenotypes]
    #list(
      [*Apollo 11/12/17 Baseline (Paul et al., 2022):* _Arabidopsis_ grown in authentic lunar regolith triggers severe ROS, salt, metal, and ionic stress transcriptomes.],
      [*PTMC Corpus Convergence (`n = 187` PDFs):* Student macro-phenotypes independently converge on the exact same physicochemical drivers:],
    )
    #table(
      columns: (2.1fr, 0.7fr, 0.8fr),
      inset: 4.5pt,
      stroke: 0.4pt + rgb("#cfdde1"),
      fill: (_, row) => if row == 0 { rgb("#d7ebf1") } else { none },
      [*Stress Bottleneck*], [*PDFs*], [*Share*],
      ..data.top_bottlenecks.slice(0, 6).map(b => (b.bottleneck, str(b.count), str(b.pct) + "%")).flatten()
    )
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#0f7f9f"))[The Coupled Biogeochemical–Hydraulic Model]
    #v(4pt)
    Why single-factor chemical NPK additions underperform (`60%` vs `92–100%` for bio-organic matrices):
    + *Physical Pore Collapse:* Angular glass/plagioclase fines in `LHS-1` pack under gravity-driven watering, inducing root hypoxia and mechanical impedance (`42.2%`).
    + *Alkaline Precipitation (`pH 8.5–10.0`):* Locks up Fe#super[2+/3+] and PO#sub[4]#super[3-], causing chlorosis even when synthetic fertilizer is present (`21.9%`).
    + *Biopolymer & Humic Chelation:* Microbial extracellular polymeric substances (EPS), necromass amino sugars, and humic acids aggregate fines into macropores while chelating micronutrients.
  ],
)

#takeaway_box(rgb("#0f7f9f"), [Regolith remediation requires simultaneous rhizosphere pH/redox buffering and micro-aggregate pore stabilization—validating dual bio-matrix ISRU architectures.])

#pagebreak()

// =========================================================================
// SLIDE 10: Stage 3 · Spring 2026 Closed-Loop ISRU Breakthroughs
// =========================================================================
#slide_header(
  "STAGE 3 · SPACE BIOLOGY, BLSS & NASA LUNAR LEAF RESEARCHERS",
  rgb("#0f7f9f"),
  "Spring 2026 Spotlight: Planetary-Protection-Compliant & Circular ISRU",
  "Exemplar student discoveries directly relevant to lunar habitat waste bioreactors",
)

#table(
  columns: (1.1fr, 0.9fr, 0.6fr, 0.8fr, 2.7fr),
  inset: 5.5pt,
  stroke: 0.45pt + rgb("#cfdde1"),
  fill: (_, row) => if row == 0 { rgb("#d7ebf1") } else { rgb("#ffffff") },
  [*Team*], [*Division*], [*Body*], [*Crop*], [*Key Bioregenerative / ISRU Finding*],
  [Team Shonik], [High School], [Lunar], [Radish], [15% w/w *heat-killed microbial necromass* in regolith increased 20-day shoot height by *125%* (`14.2` vs `6.3 cm`) and fresh biomass *4.9×* (`1.03` vs `0.21 g`).],
  [MCST Biotech 1], [High School], [Lunar], [Seedlings], [*Sodium alginate spherification* encapsulates seeds in hydrated biopolymer spheres, bypassing bulk regolith hydrophobicity.],
  [Smells fishy1!], [High School], [Lunar], [Spinach], [Combined *aquaculture effluent + hydrogel* in lunar simulant to close the fish-waste-to-crop nitrogen loop.],
  [The Marshroomers], [Professional], [Martian], [_P. ostreatus_], [Cultivated *oyster mushroom mycelium* in `MGS-1` Martian regolith for dual food production and structural biocomposite bricks.],
  [EPCC Team Artemis], [Professional], [Lunar], [Tomato / Basil], [*Banana-peel nano-fertilizer* (`n = 28` factorial array) enhanced post-germination K/P bioavailability under automated bottom-wick irrigation.],
  [Team Voyager], [Professional], [Lunar], [Lettuce], [*Chihuahuan Desert soil microbial communities* accelerated early _Lactuca sativa_ establishment under alkaline lunar regolith stress.],
)

#takeaway_box(rgb("#0f7f9f"), [*Team Shonik*'s thermally inactivated necromass paradigm is a major conceptual advance: sterile bioreactor waste can fertilize lunar regolith without live forward-contamination risks.])

#pagebreak()

// =========================================================================
// SLIDE 11: Stage 3 · Integration with NASA OSDR, TOAST & Lunar LEAF
// =========================================================================
#slide_header(
  "STAGE 3 · SPACE BIOLOGY, BLSS & NASA LUNAR LEAF RESEARCHERS",
  rgb("#0f7f9f"),
  "Connecting Citizen-Science Regolith Screening to NASA Lunar LEAF & OSDR",
  "How OBO ontology harmonization links classroom phenotype trials to spaceflight multi-omics",
)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 10pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#0f7f9f"), rest: 0.6pt + rgb("#cfdde1")), inset: 12pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#0f7f9f"))[1 · SEMANTIC TAXONOMY LINKAGE] \
    #v(4pt)
    Every focal crop in `ptm-meta` is mapped to `NCBITaxon` (`NCBITaxon:3726` _R. sativus_, `NCBITaxon:3711` _B. rapa_, `NCBITaxon:4236` _L. sativa_), enabling direct programmatic joins against *NASA OSDR* and *TOAST* transcriptomic datasets.
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#004053"), rest: 0.6pt + rgb("#cfdde1")), inset: 12pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#004053"))[2 · ENVO / AGRO / PECO ONTOLOGIES] \
    #v(4pt)
    Substrate and environmental treatments map to standard OBO URIs (`ENVO:00005750` regolith, `AGRO:00000370` microbial inoculant, `PECO:0007152` spectral lighting), aligning ground analog metadata with NASA GeneLab AWG standards.
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: (top: 4pt + rgb("#3f7d4e"), rest: 0.6pt + rgb("#cfdde1")), inset: 12pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#3f7d4e"))[3 · LUNAR LEAF DIGITAL TWINS] \
    #v(4pt)
    Provides empirical prior distributions on germination timing, alkaline pH buffering, and hydraulic crusting to parameterize *Lunar LEAF* growth chamber boundary-layer and rhizosphere models.
  ],
)

#takeaway_box(rgb("#0f7f9f"), [By adopting NASA OSDR-compatible OBO ontologies, `ptm-meta` bridges K–12/University citizen science directly into professional space-biology discovery platforms.])

#pagebreak()

// =========================================================================
// SLIDE 12: Stage 4 · AI/ML & FAIR Open-Science Engineers (Pipeline)
// =========================================================================
#slide_header(
  "STAGE 4 · COMPUTATIONAL AI/ML & FAIR OPEN-SCIENCE ENGINEERS",
  rgb("#d97706"),
  "End-to-End FAIR Architecture: From Unstructured PDFs to RO-Crate 1.1",
  "Zero-hallucination provenance, Draft 2020-12 JSON Schemas, and hybrid extraction",
)

#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 8pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#d97706"))[1. SCRAPE & SHA-256] \
    #v(3pt)
    #text(size: 9.8pt)[
      - `ptm_meta.scrape` & `fetch`
      - 24 HTML snapshots
      - `187/187` PDFs verified with 64-char SHA-256 hashes in `manifest.json`
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#d97706"))[2. PARSE & TABLE OCR] \
    #v(3pt)
    #text(size: 9.8pt)[
      - `PyMuPDF` + `pdfplumber`
      - `2,710` pages (`3.43M` chars)
      - `1,206` cell-level tables
      - Flags `2` scanned PDFs for multimodal PDF byte input
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#d97706"))[3. HYBRID EXTRACTION] \
    #v(3pt)
    #text(size: 9.8pt)[
      - Pydantic v2 `ReportExtraction`
      - Pluggable `--backend gemini` & `--backend heuristic`
      - Mandatory verbatim `evidence_quote` + `page_number` audit (`100%` match)
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 10pt, radius: 5pt)[
    #text(size: 10pt, weight: "bold", fill: rgb("#d97706"))[4. FAIR & RO-CRATE 1.1] \
    #v(3pt)
    #text(size: 9.8pt)[
      - CSV, Parquet, JSON
      - `ro-crate-metadata.json`
      - `CITATION.cff` & `codemeta.json`
      - Automated GitHub Actions CI + Pages deploy
    ]
  ],
)

#v(8pt)
#box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 10pt, radius: 6pt)[
  #text(size: 11pt, weight: "bold", fill: rgb("#004053"))[Reproducible CLI & Verification Suite (`uv` + `pytest`)] \
  #v(2pt)
  #text(size: 9.5pt, fill: rgb("#3d5a64"))[
    `uv run ptm-meta scrape && uv run ptm-meta fetch --verify && uv run ptm-meta parse && uv run ptm-meta extract --backend auto && uv run ptm-meta normalize && uv run ptm-meta build-manuscript && uv run ptm-meta build-fair`
  ]
]

#takeaway_box(rgb("#d97706"), [Every extracted trial arm is contract-validated against `schemas/experiment_record.schema.json` and traced to an exact PDF SHA-256 digest and page quote.])

#pagebreak()

// =========================================================================
// SLIDE 13: Stage 4 · Unsupervised NLP & Protocol Embedding Manifold
// =========================================================================
#slide_header(
  "STAGE 4 · COMPUTATIONAL AI/ML & FAIR OPEN-SCIENCE ENGINEERS",
  rgb("#d97706"),
  "Unsupervised Representation Learning: TF-IDF + SVD + UMAP Archetypes",
  "Jointly embedding narrative hypotheses/findings and structured experimental protocol features",
)

#grid(
  columns: (1.38fr, 1fr),
  gutter: 12pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 6pt, radius: 6pt)[
    #if data.figures_present.fig2 [
      #image("/manuscript/figures/fig2.png", width: 100%)
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 11pt, radius: 6pt)[
    #text(size: 12pt, weight: "bold", fill: rgb("#d97706"))[Clustering Pipeline Design]
    #list(
      [*Feature fusion:* `TfidfVectorizer(max_features=800, ngram_range=(1,2))` reduced via 20-D `TruncatedSVD`, concatenated with one-hot protocol vectors (`celestial_body`, `regolith_simulant`, `crop_guild`, `track`) and `StandardScaler`.],
      [*Model selection:* K-Means swept over `k = 2..10` (`n_init = 20`) maximizing Silhouette Score.],
      [*Manifold structure:* UMAP (`n_neighbors = 15`, `min_dist = 0.15`) cleanly separates lunar vs. Martian campaigns and groups microbial, organic, and hydrogel protocols.],
    )
  ],
)

#takeaway_box(rgb("#d97706"), [Joint text + protocol embeddings recover latent experimental design families across 12 years of heterogeneous student reports without manual labeling.])

#pagebreak()

// =========================================================================
// SLIDE 14: Stage 4 · Leak-Free Grouped ML & SHAP Interpretability
// =========================================================================
#slide_header(
  "STAGE 4 · COMPUTATIONAL AI/ML & FAIR OPEN-SCIENCE ENGINEERS",
  rgb("#d97706"),
  "Preventing Multi-Arm Data Leakage: Grouped CV & SHAP Attributions",
  "Grouping splits strictly by report_id with training-only ColumnTransformer pipelines",
)

#grid(
  columns: (1.28fr, 1.05fr),
  gutter: 10pt,
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 6pt, radius: 6pt)[
    #if data.figures_present.fig3 [
      #image("/manuscript/figures/fig3.png", width: 100%)
    ]
  ],
  box(width: 100%, fill: rgb("#ffffff"), stroke: 0.6pt + rgb("#cfdde1"), inset: 9pt, radius: 6pt)[
    #text(size: 11pt, weight: "bold", fill: rgb("#d97706"))[Grouped Benchmark (`n = 128` Arms, `87` Reports)]
    #v(2pt)
    #table(
      columns: (1.4fr, 1.2fr, 1.2fr, 0.7fr),
      inset: 4pt,
      stroke: 0.4pt + rgb("#cfdde1"),
      fill: (_, row) => if row == 0 { rgb("#eaf1f3") } else { none },
      [*Model*], [*CV ROC-AUC*], [*CV PR-AUC*], [*Test F1*],
      ..data.ml.models.map(m => (
        m.model,
        str(m.cv_roc_auc) + " (" + str(m.cv_roc_auc_ci.at(0)) + "–" + str(m.cv_roc_auc_ci.at(1)) + ")",
        str(m.cv_pr_auc),
        str(m.test_f1),
      )).flatten()
    )
    #v(4pt)
    #text(size: 9.5pt, fill: rgb("#3d5a64"))[
      - *Zero report leakage:* `GroupShuffleSplit` (80/20) + 5-fold `StratifiedGroupKFold` on `report_id`.
      - *Top SHAP drivers:* Amendment category, unamended regolith control presence, duration, and crop guild.
    ]
  ],
)

#takeaway_box(rgb("#d97706"), [Random Forest (`CV ROC-AUC = 0.689`, `PR-AUC = 0.915`) and HistGradientBoosting (`Test ROC-AUC = 0.595`) outperform majority baselines under strict report-level grouping.])

#pagebreak()

// =========================================================================
// SLIDE 15: Synthesis · Cross-Stakeholder Action Matrix & Portal Links
// =========================================================================
#slide_header(
  "SYNTHESIS · CROSS-STAKEHOLDER ACTION MATRIX",
  rgb("#004053"),
  "Summary of Recommendations & Live FAIR Research Portal",
  "Coordinated next steps across Program Leadership, Educators, Space Biologists, and Data Engineers",
)

#table(
  columns: (1.2fr, 1.7fr, 1.8fr),
  inset: 7pt,
  stroke: 0.45pt + rgb("#cfdde1"),
  fill: (_, row) => if row == 0 { rgb("#004053") } else { rgb("#ffffff") },
  [#text(fill: white, weight: "bold")[Stakeholder Group]],
  [#text(fill: white, weight: "bold")[Key Empirical Insight from Meta-Analysis]],
  [#text(fill: white, weight: "bold")[Immediate Action Item]],
  [*1. ICS & Space Grant Leadership*],
  [`71.7%` of teams use Earth soil controls, but only `38.0%` include a `100% unamended regolith` negative control and `15.0%` run statistical tests.],
  [Mandate the *3-Tier Control Architecture* (`Earth`, `100% Regolith`, `Treatments`) and a standardized 1-table numeric summary in future rubrics.],
  [*2. Educators, Coaches & Students*],
  [Radish (`18.2%`), bean (`10.2%`), spinach (`8.6%`), and lettuce (`7.5%`) paired with vermicompost (`100%`) or microbes (`92%`) lead success rates.],
  [Target open cells in the *Crop Guild × Amendment Sparsity Map* (e.g., alginate encapsulation + legumes; biochar + fungi) with $n >= 3$ replicates.],
  [*3. Space Biology & Lunar LEAF*],
  [Regolith sterility (`69%`), compaction/crusting (`42%`), hydrophobicity (`36%`), and alkaline pH (`22%`) require coupled bio-matrix buffering.],
  [Evaluate *thermally sterilized microbial necromass* (*Team Shonik*, `4.9×` biomass) and mycoponic biocomposites (*The Marshroomers*) in Lunar LEAF chambers.],
  [*4. AI/ML & FAIR Engineers*],
  [Heuristic table parsing guarantees `100%` quote verification offline; multi-arm correlation requires `report_id`-grouped CV (`ROC-AUC = 0.689`).],
  [Execute `ptm-meta extract --backend gemini` multimodal runs as new seasonal cohorts publish to maintain a live RO-Crate 1.1 observatory.],
)

#v(6pt)
#box(width: 100%, fill: rgb("#eaf1f3"), stroke: 0.6pt + rgb("#0f7f9f"), inset: 10pt, radius: 6pt)[
  #text(size: 10.5pt, fill: rgb("#004053"))[
    *Explore & Cite:* Live Portal `https://dr-richard-barker.github.io/Plant_the_moon/` · Manuscript PDF `.../manuscript.html` · Interactive 187-Report Explorer `.../explorer.html` · GitHub `https://github.com/dr-richard-barker/Plant_the_moon`
  ]
]
