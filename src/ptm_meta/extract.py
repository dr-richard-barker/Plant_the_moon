"""Hybrid structured extraction: Gemini structured outputs + offline heuristic baseline."""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from ptm_meta.models import (
    AmendmentCategory,
    BottleneckTag,
    CelestialBody,
    CropGuild,
    DataAvailability,
    ManifestRecord,
    OutcomeDirection,
    RegolithSimulant,
    ReportExtraction,
    TrialArm,
)

# Controlled vocabularies shared by normalization and heuristic extraction
SIMULANT_PATTERNS: list[tuple[RegolithSimulant, re.Pattern[str]]] = [
    ("LHS-1D", re.compile(r"\b(?:LHS[-\s]?1D|Lunar\s+Highlands?\s+Dust\s+Simulant)\b", re.I)),
    ("LHS-1", re.compile(r"\b(?:LHS[-\s]?1|Lunar\s+Highlands?\s+Simulant)\b", re.I)),
    ("LMS-1D", re.compile(r"\b(?:LMS[-\s]?1D|Lunar\s+Mare\s+Dust\s+Simulant)\b", re.I)),
    ("LMS-1", re.compile(r"\b(?:LMS[-\s]?1|Lunar\s+Mare\s+Simulant)\b", re.I)),
    ("JSC-1A", re.compile(r"\bJSC[-\s]?1A?\b", re.I)),
    ("MGS-1S", re.compile(r"\b(?:MGS[-\s]?1S|Mars\s+Global\s+Simulant\s+Sulfate)\b", re.I)),
    ("MGS-1", re.compile(r"\b(?:MGS[-\s]?1|Martian\s+Global\s+Simulant|Mars\s+Global\s+Simulant)\b", re.I)),
    ("MMS-2", re.compile(r"\b(?:MMS[-\s]?2|Mojave\s+Mars\s+Simulant\s*2)\b", re.I)),
    ("MMS-1", re.compile(r"\b(?:MMS[-\s]?1|Mojave\s+Mars\s+Simulant)\b", re.I)),
    ("exolith_unspecified", re.compile(r"\b(?:Exolith(?:\s+Lab)?|Space\s+Resource\s+Technologies)\b", re.I)),
]

CROP_TAXONOMY: list[tuple[str, str | None, CropGuild, re.Pattern[str]]] = [
    ("radish", "Raphanus sativus", "root", re.compile(r"\b(radish(?:es)?|raphanus\s+sativus)\b", re.I)),
    ("lettuce", "Lactuca sativa", "leafy_green", re.compile(r"\b(lettuce|lactuca\s+sativa)\b", re.I)),
    ("spinach", "Spinacia oleracea", "leafy_green", re.compile(r"\b(spinach|spinacia\s+oleracea)\b", re.I)),
    ("arugula", "Eruca vesicaria", "leafy_green", re.compile(r"\b(arugula|rocket|eruca)\b", re.I)),
    ("kale", "Brassica oleracea", "leafy_green", re.compile(r"\b(kale|brassica\s+oleracea)\b", re.I)),
    ("bok choy", "Brassica rapa", "leafy_green", re.compile(r"\b(bok\s+choy|pak\s+choi|brassica\s+rapa)\b", re.I)),
    ("green bean", "Phaseolus vulgaris", "legume", re.compile(r"\b(green\s+bean|bush\s+bean|snap\s+bean|purple\s+bean|phaseolus\s+vulgaris|bean)\b", re.I)),
    ("mung bean", "Vigna radiata", "legume", re.compile(r"\b(mung\s+bean|vigna\s+radiata)\b", re.I)),
    ("cowpea", "Vigna unguiculata", "legume", re.compile(r"\b(cowpea|vigna\s+unguiculata|black[-\s]?eyed\s+pea)\b", re.I)),
    ("pea", "Pisum sativum", "legume", re.compile(r"\b(pea(?:s)?|pisum\s+sativum|sugar\s+snap)\b", re.I)),
    ("soybean", "Glycine max", "legume", re.compile(r"\b(soybean|edamame|glycine\s+max)\b", re.I)),
    ("clover", "Trifolium spp.", "legume", re.compile(r"\b(clover|trifolium|alfalfa|medicago)\b", re.I)),
    ("oyster mushroom", "Pleurotus ostreatus", "fungi", re.compile(r"\b(pleurotus|oyster\s+mushroom|lion'?s\s+mane|hericium|mycelium|mushroom)\b", re.I)),
    ("tomato", "Solanum lycopersicum", "fruiting", re.compile(r"\b(tomato(?:es)?|solanum\s+lycopersicum|micro\s?tom)\b", re.I)),
    ("cucumber", "Cucumis sativus", "fruiting", re.compile(r"\b(cucumber|cucumis\s+sativus)\b", re.I)),
    ("pepper", "Capsicum annuum", "fruiting", re.compile(r"\b(pepper|capsicum)\b", re.I)),
    ("strawberry", "Fragaria ananassa", "fruiting", re.compile(r"\b(strawberr(?:y|ies)|fragaria)\b", re.I)),
    ("basil", "Ocimum basilicum", "herb", re.compile(r"\b(basil|ocimum\s+basilicum)\b", re.I)),
    ("cilantro", "Coriandrum sativum", "herb", re.compile(r"\b(cilantro|coriander|coriandrum)\b", re.I)),
    ("collard greens", "Brassica oleracea", "leafy_green", re.compile(r"\b(collard\s+greens?|swiss\s+chard|miner['’]?s\s+lettuce|claytonia|water\s+spinach|ipomoea\s+aquatica)\b", re.I)),
    ("purslane", "Portulaca oleracea", "leafy_green", re.compile(r"\b(purslane|portulaca\s+oleracea)\b", re.I)),
    ("scallion", "Allium fistulosum", "other", re.compile(r"\b(scallion|allium\s+fistulosum|onion|garlic|chive)\b", re.I)),
    ("carrot", "Daucus carota", "root", re.compile(r"\b(carrot|daucus\s+carota)\b", re.I)),
    ("beet", "Beta vulgaris", "root", re.compile(r"\b(beet(?:s|root)?|beta\s+vulgaris)\b", re.I)),
    ("potato", "Solanum tuberosum", "root", re.compile(r"\b(potato(?:es)?|solanum\s+tuberosum)\b", re.I)),
    ("turnip", "Brassica rapa", "root", re.compile(r"\b(turnip)\b", re.I)),
    ("rice", "Oryza sativa", "grain", re.compile(r"\b(rice|oryza\s+sativa)\b", re.I)),
    ("wheat", "Triticum aestivum", "grain", re.compile(r"\b(wheat|wheatgrass|triticum|oat(?:s)?|barley|rye|quinoa|amaranth(?:us)?)\b", re.I)),
    ("corn", "Zea mays", "grain", re.compile(r"\b(corn|maize|zea\s+mays)\b", re.I)),
    ("microgreens", None, "microgreen", re.compile(r"\b(microgreen(?:s)?|garden\s+cress|cress|mustard\s+green)\b", re.I)),
    ("sunflower", "Helianthus annuus", "other", re.compile(r"\b(sunflower|helianthus|yarrow|achillea|dandelion|opuntia|cact(?:us|i)|water\s+lil(?:y|ies)|nymphaea)\b", re.I)),
    ("marigold", "Tagetes spp.", "other", re.compile(r"\b(marigold|arabidopsis)\b", re.I)),
]

AMENDMENT_RULES: list[tuple[AmendmentCategory, re.Pattern[str]]] = [
    ("hydrogel_alginate_polymer", re.compile(r"\b(hydrogel|alginate|sodium\s+alginate|superabsorbent|polymer|agar)\b", re.I)),
    ("vermicompost_aquaculture", re.compile(r"\b(vermicompost|aquaculture|aquaponic|worm\s+castings?|frass|fish\s+emulsion)\b", re.I)),
    ("microbial_mycorrhizal", re.compile(r"\b(mycorrhiz\w*|rhizobi\w*|microb\w+|bacteria|bacillus|azospirillum|inocul\w+|necromass|cyanobacter\w*)\b", re.I)),
    ("biochar_carbon", re.compile(r"\b(biochar|activated\s+carbon|humic|fulvic)\b", re.I)),
    ("nano_fertilizer_mineral", re.compile(r"\b(nano[-\s]?fertilizer|nanoparticle|zeolite|gypsum|lime|sulfur|basalt\s+dust)\b", re.I)),
    ("plant_extract_waste", re.compile(r"\b(banana\s+peel|coffee\s+ground|tea\s+leaves?|kelp|seaweed|algae|food\s+waste)\b", re.I)),
    ("coir_peat_perlite_substrate", re.compile(r"\b(coco\s+coir|coir|peat\s+moss|perlite|vermiculite|sphagnum|rockwool)\b", re.I)),
    ("organic_compost_manure", re.compile(r"\b(compost|manure|organic\s+fertilizer|humus|biosolid)\b", re.I)),
    ("synthetic_fertilizer_hydroponic", re.compile(r"\b(npk|miracle[-\s]?gro|hoagland|hydroponic|synthetic\s+fertilizer|osmocote|nutrient\s+solution)\b", re.I)),
    ("light_spectrum_env", re.compile(r"\b(wavelength|led\s+spectrum|red\s+light|blue\s+light|photoperiod|uv\s+light)\b", re.I)),
]

BOTTLENECK_RULES: list[tuple[BottleneckTag, re.Pattern[str]]] = [
    ("alkaline_ph", re.compile(r"\b(high\s+ph|alkaline|ph\s*(?:of\s*)?(?:8|9|10|11)|acidif)\b", re.I)),
    ("compaction_crusting", re.compile(r"\b(compact\w*|crust\w*|hard\s+surface|density|aeration|porosity)\b", re.I)),
    ("hydrophobicity_water_retention", re.compile(r"\b(hydrophob|water\s+retention|drainage|desiccat|moisture\s+loss|dry\s+out)\b", re.I)),
    ("nutrient_deficiency", re.compile(r"\b(nutrient\s+deficien|nitrogen|phosphorus|potassium|organic\s+matter|sterile|lack\s+of\s+nutrients)\b", re.I)),
    ("heavy_metals_or_salinity", re.compile(r"\b(perchlorate|heavy\s+metal|salinit|toxic|aluminum|iron\s+oxide)\b", re.I)),
    ("microbial_contamination", re.compile(r"\b(mold|fungal\s+growth|contaminat\w*|pathogen|rot)\b", re.I)),
    ("germination_failure", re.compile(r"\b(fail(?:ed)?\s+to\s+germinate|no\s+germination|0%\s+germination|poor\s+germination)\b", re.I)),
    ("light_or_temperature_stress", re.compile(r"\b(temperature|cold\s+stress|heat\s+stress|insufficient\s+light|etiolat)\b", re.I)),
    ("root_restriction", re.compile(r"\b(root\s+growth|stunted\s+root|shallow\s+root|root\s+penetration)\b", re.I)),
]

STAT_TEST_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ANOVA", re.compile(r"\banova\b", re.I)),
    ("t-test", re.compile(r"\bt[-\s]?test\b", re.I)),
    ("Tukey HSD", re.compile(r"\btukey\b", re.I)),
    ("Chi-square", re.compile(r"\bchi[-\s]?square\b", re.I)),
    ("Linear Regression", re.compile(r"\b(linear\s+regression|r\^?2\s*=)\b", re.I)),
    ("Standard Deviation / Error", re.compile(r"\b(standard\s+deviation|std\s+dev|standard\s+error|error\s+bars)\b", re.I)),
    ("p-value", re.compile(r"\bp\s*[<>≤=]\s*0\.\d+", re.I)),
]


def _load_env() -> None:
    """Load credentials cleanly from project .env and ~/.env without printing secrets."""
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".env", override=False)


def available_gemini_key() -> bool:
    _load_env()
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def _first_quote(pages: list[dict[str, Any]], pattern: re.Pattern[str]) -> tuple[str | None, int | None]:
    for p in pages:
        txt = p.get("text", "")
        for sent in re.split(r"(?<=[.!?])\s+|\n", txt):
            s = " ".join(sent.split()).strip()
            if 20 <= len(s) <= 450 and pattern.search(s):
                return s, int(p["page_number"])
    return None, None


def _infer_celestial_body(title: str | None, pages: list[dict[str, Any]]) -> CelestialBody:
    """Classify target regolith using title & early-page weighting to prevent Intro boilerplate bias."""
    lunar_pat = re.compile(r"\b(lunar|moon|lhs-?1|lms-?1|jsc-?1a)\b", re.I)
    martian_pat = re.compile(r"\b(mars|martian|mgs-?1|mms-?[12])\b", re.I)

    lunar_score = 10 * len(lunar_pat.findall(title or ""))
    martian_score = 10 * len(martian_pat.findall(title or ""))
    for i, pg in enumerate(pages):
        w = 3 if i < 2 else 1
        txt = pg.get("text", "")
        lunar_score += w * len(lunar_pat.findall(txt))
        martian_score += w * len(martian_pat.findall(txt))

    if lunar_score == 0 and martian_score == 0:
        return "unspecified"
    if lunar_score >= 6 and martian_score >= 6:
        ratio = max(lunar_score, martian_score) / max(1, min(lunar_score, martian_score))
        if ratio <= 2.2:
            return "both"
    return "lunar" if lunar_score >= martian_score else "martian"


def _extract_table_metrics(pages: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Parse structured numerical summaries (germination %, height cm, biomass g, pH) from PDF tables."""
    summary: dict[str, dict[str, float]] = {}

    def _first_float(cell: str, lo: float, hi: float) -> float | None:
        m = re.search(r"(\d+(?:\.\d+)?)", cell)
        if not m:
            return None
        val = float(m.group(1))
        return val if lo <= val <= hi else None

    for pg in pages:
        for tbl in pg.get("tables", []):
            if len(tbl) < 2:
                continue
            hdr = " | ".join(tbl[0]).lower()
            is_germ = "germinat" in hdr
            is_height = "height" in hdr or "cm" in hdr
            is_mass = "biomass" in hdr or "weight" in hdr or "mass" in hdr
            is_ph = "ph" in hdr
            if not (is_germ or is_height or is_mass or is_ph):
                continue

            # Identify target metric column if header gives column clues
            col_targets: dict[int, tuple[str, float, float]] = {}
            for ci, cell in enumerate(tbl[0]):
                cl = cell.lower()
                if "germinat" in cl:
                    col_targets[ci] = ("germination_rate_pct", 0.0, 100.0)
                elif "height" in cl or "(cm)" in cl:
                    col_targets[ci] = ("mean_shoot_height_cm", 0.01, 150.0)
                elif "biomass" in cl or "weight" in cl:
                    col_targets[ci] = ("mean_fresh_biomass_g", 0.001, 500.0)
                elif re.search(r"\bph\b", cl):
                    col_targets[ci] = ("substrate_ph", 2.0, 12.0)

            for row in tbl[1:]:
                row_label = (row[0] if row else "").lower()
                if not row_label:
                    continue
                bucket: str | None = None
                if any(k in row_label for k in ("earth", "potting", "garden", "positive")):
                    bucket = "earth_soil_control"
                elif any(k in row_label for k in ("control", "100% regolith", "unamended", "pure regolith")):
                    bucket = "none_control"
                else:
                    for cat, pat in AMENDMENT_RULES:
                        if pat.search(row_label):
                            bucket = cat
                            break
                if not bucket:
                    continue
                vals = summary.setdefault(bucket, {})
                if col_targets:
                    for ci, (field, lo, hi) in col_targets.items():
                        if ci < len(row):
                            v = _first_float(row[ci], lo, hi)
                            if v is not None and field not in vals:
                                vals[field] = v
                else:
                    # Time-series table (like Shonik Table 1): take last non-empty numeric column
                    last_num: float | None = None
                    for cell in reversed(row[1:]):
                        v = _first_float(cell, 0.0, 150.0)
                        if v is not None:
                            last_num = v
                            break
                    if last_num is not None:
                        if is_germ and "germination_rate_pct" not in vals and last_num <= 100.0:
                            vals["germination_rate_pct"] = last_num
                        elif is_height and "mean_shoot_height_cm" not in vals:
                            vals["mean_shoot_height_cm"] = last_num
                        elif is_mass and "mean_fresh_biomass_g" not in vals:
                            vals["mean_fresh_biomass_g"] = last_num

    return summary


def _local_outcome_vs_control(
    full_text: str,
    pat: re.Pattern[str],
    trt_metrics: dict[str, float],
    ctrl_metrics: dict[str, float],
) -> OutcomeDirection:
    """Estimate treatment outcome polarity using numerical control comparison or local text window."""
    for metric in ("germination_rate_pct", "mean_shoot_height_cm", "mean_fresh_biomass_g"):
        if metric in trt_metrics and metric in ctrl_metrics and ctrl_metrics[metric] > 0:
            ratio = trt_metrics[metric] / ctrl_metrics[metric]
            if ratio >= 1.1:
                return "improved"
            if ratio <= 0.9:
                return "reduced"
            return "neutral"

    m = pat.search(full_text)
    if not m:
        return "not_reported"
    window = full_text[max(0, m.start() - 250) : min(len(full_text), m.end() + 350)]
    pos = len(re.findall(r"\b(improv\w*|increas\w*|higher|outperform\w*|greater|best|enhanced|tallest)\b", window, re.I))
    neg = len(re.findall(r"\b(inhibit\w*|toxic\w*|died|failed|lower\s+than|worse|stunted|reduce[sd]?)\b", window, re.I))
    if pos > neg:
        return "improved"
    if neg > pos:
        return "reduced"
    return "not_reported"


def extract_heuristic(rec: ManifestRecord, parsed: dict[str, Any]) -> ReportExtraction:
    """Deterministic offline structured extraction from parsed PDF text & tables."""
    pages = parsed.get("pages", [])
    full_text = "\n".join(p.get("text", "") for p in pages)
    title_and_text = f"{rec.project_title or ''}\n{full_text}"

    celestial = _infer_celestial_body(rec.project_title, pages)

    # Simulant
    simulant: RegolithSimulant = "unspecified"
    simulant_raw: str | None = None
    for code, pat in SIMULANT_PATTERNS:
        m = pat.search(title_and_text)
        if m:
            simulant = code
            simulant_raw = m.group(0)
            break

    # Crops (pick most frequent hit)
    crop_hits: list[tuple[int, str, str | None, CropGuild]] = []
    for common, sci, guild, pat in CROP_TAXONOMY:
        cnt = len(pat.findall(title_and_text))
        if cnt > 0:
            if rec.project_title and pat.search(rec.project_title):
                cnt += 5
            crop_hits.append((cnt, common, sci, guild))
    crop_hits.sort(reverse=True)
    if crop_hits:
        _, crop_common, crop_sci, crop_guild = crop_hits[0]
        if len(crop_hits) >= 2 and crop_hits[1][0] >= 3 and crop_hits[1][3] != crop_guild:
            crop_guild = "mixed"
    else:
        crop_common, crop_sci, crop_guild = "unspecified", None, "unspecified"

    # Duration
    dur_days: float | None = None
    m_days = re.search(r"\b(\d{1,3})\s*[-]?\s*day(?:s)?\b", full_text, re.I)
    m_weeks = re.search(r"\b(\d{1,2})\s*[-]?\s*week(?:s)?\b", full_text, re.I)
    if m_days and 5 <= int(m_days.group(1)) <= 365:
        dur_days = float(m_days.group(1))
    elif m_weeks and 1 <= int(m_weeks.group(1)) <= 52:
        dur_days = float(int(m_weeks.group(1)) * 7)

    # Controls
    has_earth_ctrl = bool(re.search(r"\b(potting\s+(?:soil|mix)|earth\s+soil|garden\s+soil|positive\s+control|control\s+soil)\b", full_text, re.I))
    has_reg_ctrl = bool(re.search(r"\b(100%\s*(?:lunar|martian|regolith|simulant|lhs|mgs|lms)|unamended|pure\s+regolith|regolith\s+control|negative\s+control)\b", full_text, re.I))

    # Statistical tests
    stats_used = [name for name, pat in STAT_TEST_PATTERNS if pat.search(full_text)]

    # Data availability
    n_tables = parsed.get("table_count", 0)
    if n_tables > 0:
        data_avail: DataAvailability = "summary_means"
    elif parsed.get("parse_quality") == "image_or_scanned":
        data_avail = "charts_only"
    elif re.search(r"\b(cm|mm|grams?|g\b|%)\b", full_text, re.I):
        data_avail = "summary_means"
    else:
        data_avail = "qualitative_only"

    # Bottlenecks
    bottlenecks = [tag for tag, pat in BOTTLENECK_RULES if pat.search(full_text)]

    # Hypothesis & summary sentence extraction
    hyp_q, _ = _first_quote(pages, re.compile(r"\bhypothes|predict|we\s+expect|objective\b", re.I))
    conc_q, _ = _first_quote(pages, re.compile(r"\bconclu|results\s+(?:show|indicate|demonstrate)|overall|found\s+that\b", re.I))
    summary = conc_q or (rec.project_title or f"{rec.team_name} ({rec.season}) investigated {crop_common} in {celestial} regolith.")

    # Table-parsed numerical metrics
    tbl_metrics = _extract_table_metrics(pages)
    ctrl_metrics = tbl_metrics.get("none_control", {})
    earth_metrics = tbl_metrics.get("earth_soil_control", {})

    # Optional text-level pH fallback
    m_ph = re.search(r"\bpH\s*(?:of|was|is|=|:)?\s*(\d(?:\.\d+)?)", full_text)
    fallback_ph = float(m_ph.group(1)) if m_ph and 2.5 <= float(m_ph.group(1)) <= 12.0 else None

    arms: list[TrialArm] = []
    if has_earth_ctrl:
        eq, ep = _first_quote(pages, re.compile(r"\bpotting\s+(?:soil|mix)|earth\s+soil|positive\s+control\b", re.I))
        arms.append(
            TrialArm(
                arm_id="arm_ctrl_earth",
                arm_label="Earth Soil Control",
                is_control=True,
                control_type="earth_soil",
                regolith_pct=0.0,
                amendment_category="earth_soil_control",
                germination_rate_pct=earth_metrics.get("germination_rate_pct"),
                mean_shoot_height_cm=earth_metrics.get("mean_shoot_height_cm"),
                mean_fresh_biomass_g=earth_metrics.get("mean_fresh_biomass_g"),
                substrate_ph=earth_metrics.get("substrate_ph"),
                outcome_vs_regolith_control="not_reported",
                evidence_quote=eq,
                page_number=ep,
            )
        )
    if has_reg_ctrl:
        rq, rp = _first_quote(pages, re.compile(r"\b100%\s*(?:regolith|simulant|lhs|mgs|lms)|unamended|negative\s+control|pure\s+regolith\b", re.I))
        arms.append(
            TrialArm(
                arm_id="arm_ctrl_regolith",
                arm_label="Unamended Regolith Control",
                is_control=True,
                control_type="unamended_regolith",
                regolith_pct=100.0,
                amendment_category="none_control",
                germination_rate_pct=ctrl_metrics.get("germination_rate_pct"),
                mean_shoot_height_cm=ctrl_metrics.get("mean_shoot_height_cm"),
                mean_fresh_biomass_g=ctrl_metrics.get("mean_fresh_biomass_g"),
                substrate_ph=ctrl_metrics.get("substrate_ph") or fallback_ph,
                outcome_vs_regolith_control="neutral",
                evidence_quote=rq,
                page_number=rp,
            )
        )

    matched_amendments: list[tuple[AmendmentCategory, re.Pattern[str]]] = []
    for cat, pat in AMENDMENT_RULES:
        if pat.search(title_and_text):
            matched_amendments.append((cat, pat))

    if not matched_amendments:
        matched_amendments = [("other", re.compile(r"\b(treatment|soil|regolith)\b", re.I))]

    for idx, (cat, pat) in enumerate(matched_amendments[:4], start=1):
        q, pg = _first_quote(pages, pat)
        m_detail = pat.search(title_and_text)
        detail = m_detail.group(0) if m_detail else cat
        trt_m = dict(tbl_metrics.get(cat, {}))

        # Cautious germination rate capture in quote sentence or nearby text
        if "germination_rate_pct" not in trt_m and q:
            mg = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%\s*(?:germinat|sprout)", q, re.I)
            if not mg:
                mg = re.search(r"germinat\w*\s*(?:rate|was|of|:)?\s*(\d{1,3}(?:\.\d+)?)\s*%", q, re.I)
            if mg and 0.0 <= float(mg.group(1)) <= 100.0:
                trt_m["germination_rate_pct"] = float(mg.group(1))

        outcome = _local_outcome_vs_control(full_text, pat, trt_m, ctrl_metrics)
        arms.append(
            TrialArm(
                arm_id=f"arm_trt_{idx}",
                arm_label=f"Treatment ({detail})",
                is_control=False,
                control_type="none",
                amendment_category=cat,
                amendment_detail=detail,
                germination_rate_pct=trt_m.get("germination_rate_pct"),
                mean_shoot_height_cm=trt_m.get("mean_shoot_height_cm"),
                mean_fresh_biomass_g=trt_m.get("mean_fresh_biomass_g"),
                substrate_ph=trt_m.get("substrate_ph"),
                outcome_vs_regolith_control=outcome,
                evidence_quote=q,
                page_number=pg,
            )
        )

    return ReportExtraction(
        report_id=rec.report_id,
        extraction_method="heuristic",
        model_name="table-aware-lexicon-v2",
        celestial_body=celestial,
        regolith_simulant=simulant,
        regolith_simulant_raw=simulant_raw,
        crop_common_name=crop_common,
        crop_scientific_name=crop_sci,
        crop_guild=crop_guild,
        experimental_duration_days=dur_days,
        has_earth_soil_control=has_earth_ctrl,
        has_unamended_regolith_control=has_reg_ctrl,
        statistical_tests_reported=stats_used,
        data_availability=data_avail,
        primary_bottlenecks=bottlenecks,
        innovation_tags=[cat for cat, _ in matched_amendments[:4]],
        key_hypothesis=hyp_q,
        summary_findings=summary[:600],
        arms=arms,
    )


def _build_gemini_prompt(rec: ManifestRecord, parsed: dict[str, Any]) -> str:
    pages = parsed.get("pages", [])
    chunks: list[str] = []
    for p in pages[:40]:
        t = p.get("text", "")
        tbls = p.get("tables", [])
        block = f"[PAGE {p['page_number']}]\n{t[:3200]}"
        if tbls:
            block += f"\n[TABLES ON PAGE {p['page_number']}]\n{json.dumps(tbls[:3])[:2500]}"
        chunks.append(block)
    body = "\n\n".join(chunks)[:65000]

    return (
        "You are an expert astrobotany & agricultural meta-analysis extractor. "
        "Extract structured scientific metadata and EVERY distinct experimental treatment/control arm "
        "from this Plant the Moon Challenge student report.\n\n"
        f"Metadata:\n- report_id: {rec.report_id}\n- season: {rec.season}\n"
        f"- team_name: {rec.team_name}\n- division: {rec.division}\n"
        f"- project_title: {rec.project_title or 'N/A'}\n\n"
        "Strict Grounding Rules:\n"
        "1. Set report_id exactly to the value above and extraction_method='gemini_structured'.\n"
        "2. Do NOT fabricate numbers. Leave quantitative metrics null if not explicitly reported.\n"
        "3. Every arm with extracted numbers or outcomes MUST include a short verbatim `evidence_quote` "
        "copied directly from the report and the 1-based `page_number`.\n"
        "4. Separate Earth soil controls, unamended 100% regolith controls, and amended/treated arms.\n\n"
        f"Report Content:\n{body}"
    )


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=20), reraise=True)
def extract_gemini(
    rec: ManifestRecord,
    parsed: dict[str, Any],
    repo_root: Path,
    model_name: str = "gemini-2.5-flash",
) -> ReportExtraction:
    """Call Gemini Structured Outputs API (supports multimodal PDF bytes for scanned/chart decks)."""
    from google import genai
    from google.genai import types

    _load_env()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY / GOOGLE_API_KEY in environment or ~/.env")

    client = genai.Client(api_key=api_key)
    prompt = _build_gemini_prompt(rec, parsed)

    contents: list[Any] = [prompt]
    # Attach native PDF bytes when text layer is sparse/scanned or tables are missing
    if rec.local_pdf_path and parsed.get("parse_quality") != "digital_text":
        pdf_path = repo_root / rec.local_pdf_path
        if pdf_path.exists() and pdf_path.stat().st_size <= 18 * 1024 * 1024:
            contents.insert(
                0,
                types.Part.from_bytes(data=pdf_path.read_bytes(), mime_type="application/pdf"),
            )

    resp = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReportExtraction,
            temperature=0.1,
        ),
    )
    data = json.loads(resp.text)
    data["report_id"] = rec.report_id
    data["extraction_method"] = "gemini_structured"
    data["model_name"] = model_name
    return ReportExtraction.model_validate(data)


def verify_quote_provenance(extraction: ReportExtraction, parsed: dict[str, Any]) -> dict[str, Any]:
    """Audit how many arm evidence quotes match the extracted PDF text."""
    pages_norm = {
        int(p["page_number"]): re.sub(r"\s+", " ", p.get("text", "").lower())
        for p in parsed.get("pages", [])
    }
    all_norm = " ".join(pages_norm.values())
    checked = 0
    matched = 0
    for arm in extraction.arms:
        if not arm.evidence_quote:
            continue
        checked += 1
        q_norm = re.sub(r"\s+", " ", arm.evidence_quote.lower()).strip()
        snippet = q_norm[:45]
        if snippet and (
            snippet in all_norm
            or (arm.page_number and snippet in pages_norm.get(arm.page_number, ""))
        ):
            matched += 1
    return {
        "quotes_checked": checked,
        "quotes_matched": matched,
        "quote_match_rate": round(matched / checked, 3) if checked else None,
    }


def _process_one_extraction(
    rec: ManifestRecord,
    parsed_dir: Path,
    out_dir: Path,
    repo_root: Path,
    chosen: str,
    model_name: str,
    force: bool,
) -> dict[str, Any] | None:
    out_path = out_dir / f"{rec.report_id}.json"
    parsed_path = parsed_dir / f"{rec.report_id}.json"
    if not parsed_path.exists():
        return None
    parsed = json.loads(parsed_path.read_text(encoding="utf-8"))

    if out_path.exists() and not force:
        cached = json.loads(out_path.read_text(encoding="utf-8"))
        if not (chosen == "gemini" and cached.get("extraction", {}).get("extraction_method") == "heuristic"):
            return cached

    if chosen == "gemini":
        ext = extract_gemini(rec, parsed, repo_root=repo_root, model_name=model_name)
    else:
        ext = extract_heuristic(rec, parsed)

    audit = verify_quote_provenance(ext, parsed)
    payload = {"extraction": ext.model_dump(), "provenance_audit": audit}
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def extract_all(
    manifest_json: Path,
    parsed_dir: Path,
    out_dir: Path,
    repo_root: Path,
    backend: str = "auto",
    model_name: str = "gemini-2.5-flash",
    limit: int | None = None,
    force: bool = False,
    max_workers: int = 4,
) -> list[dict[str, Any]]:
    """Run hybrid extraction across parsed PDFs with incremental caching."""
    records = [
        ManifestRecord.model_validate(item)
        for item in json.loads(manifest_json.read_text(encoding="utf-8"))
        if item.get("has_pdf") and item.get("local_pdf_path")
    ]
    if limit is not None:
        records = records[:limit]

    chosen = backend
    if chosen == "auto":
        chosen = "gemini" if available_gemini_key() else "heuristic"

    out_dir.mkdir(parents=True, exist_ok=True)
    workers = max_workers if chosen == "gemini" else 1
    results: list[dict[str, Any]] = []

    if workers == 1:
        for rec in records:
            res = _process_one_extraction(
                rec, parsed_dir, out_dir, repo_root, chosen, model_name, force
            )
            if res is not None:
                results.append(res)
    else:
        ordered: dict[int, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = {
                pool.submit(
                    _process_one_extraction,
                    rec,
                    parsed_dir,
                    out_dir,
                    repo_root,
                    chosen,
                    model_name,
                    force,
                ): idx
                for idx, rec in enumerate(records)
            }
            for fut in as_completed(futs):
                res = fut.result()
                if res is not None:
                    ordered[futs[fut]] = res
        results = [ordered[i] for i in sorted(ordered)]

    return results
