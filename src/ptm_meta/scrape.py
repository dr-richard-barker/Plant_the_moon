"""Scraper for Plant the Moon Challenge awards archive pages (2021-2026)."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
import pandas as pd
import yaml
from bs4 import BeautifulSoup, Tag

from ptm_meta.models import ManifestRecord

DIVISION_RE = re.compile(
    r"^(?:Elementary|Middle|High\s+School|Professional|Undergraduate|University|College|K-?12|Family|Community)"
    r"(?:\s+School)?(?:\s+Level)?$",
    re.I,
)
CATEGORY_RE = re.compile(
    r"^(Experimental Design|Innovation|Plant Growth|Evaluation of Results|"
    r"Best\s+in\s+Show|Overall\s+Winner|People'?s\s+Choice|Honorable\s+Mention|"
    r"Engineering|Research|Science|Outreach)$",
    re.I,
)
STATE_HEADING_RE = re.compile(
    r"^Top\s+(?:([A-Z]{2,3}|Intl|International)|Elementary(?:\s+School)?|Middle(?:\s+School)?|High(?:\s+School)?|Professional)\s+Team$",
    re.I,
)
SPACE_GRANT_RE = re.compile(r"^([A-Z]{2})\s+Space\s+Grant$", re.I)
BANNER_SKIP_RE = re.compile(
    r"^(best\s+in\s+show(?:\s+winners)?|state\s+award\s+winners|"
    r"nasa\s+space\s+grant.*winners|honorable\s+mentions?)$",
    re.I,
)
LOCATION_RE = re.compile(r"^([A-Za-z .'\-]+),\s*([A-Z]{2}|[A-Za-z .'\-]+)$")
SEASON_URL_RE = re.compile(r"https://plantthemoon\.com(?:/(jr))?/awards-(spring|summer|fall)(\d{2})/?", re.I)


@dataclass(frozen=True)
class SeasonTarget:
    season: str
    slug: str
    year: int
    term: str
    order: int
    track: str
    url: str


def _fix_mojibake(txt: str) -> str:
    if any(seq in txt for seq in ("â€™", "â€œ", "â€", "â€“", "â€”", "Ã")):
        for enc in ("cp1252", "latin-1"):
            try:
                return txt.encode(enc).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
    return txt


def _clean_text(node: Tag | str | None) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return re.sub(r"\s+", " ", _fix_mojibake(node)).strip()
    # Replace <br> with space so multi-line Elementor titles don't glue words together
    html_str = str(node)
    html_str = re.sub(r"<br\s*/?>", " ", html_str, flags=re.I)
    soup = BeautifulSoup(html_str, "lxml")
    txt = _fix_mojibake(soup.get_text(" ", strip=True))
    # Fix soft-hyphen / split hyphenated lines like "Astro- Family" -> "Astro-Family"
    txt = re.sub(r"-\s+", "-", txt)
    return re.sub(r"\s+", " ", txt).strip()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "team"


def make_report_id(season_slug: str, track: str, team_name: str, pdf_url: str | None) -> str:
    """Create a deterministic, URL-safe unique report identifier."""
    base = f"{season_slug}-{track}-{_slugify(team_name)}"
    seed = pdf_url or f"{season_slug}:{track}:{team_name}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:6]
    return f"{base}-{digest}"


def load_season_targets(config_path: Path) -> tuple[list[SeasonTarget], bool]:
    """Load target archive URLs from configs/seasons.yaml."""
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    targets: list[SeasonTarget] = []
    for entry in cfg.get("seasons", []):
        for track, key in (("main", "main_url"), ("junior", "junior_url")):
            url = entry.get(key)
            if url:
                targets.append(
                    SeasonTarget(
                        season=entry["season"],
                        slug=entry["slug"],
                        year=int(entry["year"]),
                        term=entry["term"],
                        order=int(entry["order"]),
                        track=track,
                        url=url,
                    )
                )
    return targets, bool(cfg.get("discover_additional_seasons", False))


def discover_extra_targets(html: str, existing_urls: set[str]) -> list[SeasonTarget]:
    """Discover any awards season links in navigation/footer not yet in seasons.yaml."""
    discovered: list[SeasonTarget] = []
    term_map = {"spring": ("Spring", 1), "summer": ("Summer", 2), "fall": ("Fall", 3)}
    for m in SEASON_URL_RE.finditer(html):
        url = m.group(0).rstrip("/") + "/"
        if url in existing_urls:
            continue
        existing_urls.add(url)
        track = "junior" if m.group(1) else "main"
        term_raw = m.group(2).lower()
        yr_two = int(m.group(3))
        year = 2000 + yr_two
        term, term_idx = term_map[term_raw]
        slug = f"{term_raw}{yr_two:02d}"
        order = (year - 2021) * 3 + term_idx
        discovered.append(
            SeasonTarget(
                season=f"{term} {year}",
                slug=slug,
                year=year,
                term=term,
                order=order,
                track=track,
                url=url,
            )
        )
    return discovered


def _parse_location(raw: str | None) -> tuple[str | None, str | None]:
    if not raw:
        return None, None
    m = LOCATION_RE.match(raw.strip())
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def _extract_column_record(
    col: Tag,
    target: SeasonTarget,
    section_tier: str,
) -> list[ManifestRecord]:
    """Parse a single Elementor column widget card into one or more ManifestRecords."""
    # Find PDF link if any
    pdf_a = None
    for a in col.find_all("a", href=True):
        href = urljoin(target.url, a["href"].strip())
        if ".pdf" in href.lower():
            pdf_a = href
            break

    # Headings inside this card
    headings = [
        _clean_text(h)
        for h in col.select(".elementor-widget-heading .elementor-heading-title, h1, h2, h3, h4")
    ]
    headings = [h for h in headings if h]

    # Text paragraphs inside text-editor widgets
    text_blocks: list[str] = []
    for widget in col.select(".elementor-widget-text-editor .elementor-widget-container"):
        ps = [_clean_text(p) for p in widget.find_all(["p", "li", "div"], recursive=False)]
        ps = [p for p in ps if p]
        if ps:
            text_blocks.extend(ps)
        else:
            raw_t = _clean_text(widget)
            if raw_t:
                text_blocks.append(raw_t)

    # Fallback if text isn't inside text-editor widgets (older WordPress layouts)
    if not text_blocks:
        for p in col.find_all("p"):
            t = _clean_text(p)
            if t and t.lower() != "report":
                text_blocks.append(t)

    if not headings and not pdf_a:
        return []

    heading_primary = headings[0] if headings else ""
    if BANNER_SKIP_RE.match(heading_primary) and not pdf_a:
        return []

    # Image thumbnail
    img = col.find("img")
    thumb_url = None
    if img:
        thumb_url = img.get("data-src") or img.get("src")
        if thumb_url and thumb_url.startswith("data:image"):
            thumb_url = None
        if thumb_url:
            thumb_url = urljoin(target.url, thumb_url)

    division = "Elementary/Middle School" if target.track == "junior" else "High School / Professional"
    award_category: str | None = None
    project_title: str | None = None
    location_raw: str | None = None
    remaining_texts: list[str] = []

    for txt in text_blocks:
        if DIVISION_RE.match(txt):
            division = txt
        elif CATEGORY_RE.match(txt):
            award_category = txt
        elif LOCATION_RE.match(txt) and len(txt) < 60:
            location_raw = txt
        else:
            remaining_texts.append(txt)

    state_match = STATE_HEADING_RE.match(heading_primary)
    sg_match = SPACE_GRANT_RE.match(heading_primary)

    # Space Grant card lists multiple winning team names in separate <p> elements
    if sg_match and not pdf_a and remaining_texts:
        sg_state = sg_match.group(1).upper()
        badge = f"Space Grant Award: {heading_primary}"
        out: list[ManifestRecord] = []
        for tname in remaining_texts:
            out.append(
                ManifestRecord(
                    report_id=make_report_id(target.slug, target.track, f"{sg_state}-{tname}", None),
                    season=target.season,
                    season_slug=target.slug,
                    season_order=target.order,
                    year=target.year,
                    term=target.term,  # type: ignore[arg-type]
                    track=target.track,  # type: ignore[arg-type]
                    division=division,
                    award_tier="Space Grant Award",
                    award_category=heading_primary,
                    award_badges=[badge],
                    team_name=tname,
                    project_title=None,
                    location_raw=sg_state,
                    location_city=None,
                    location_state=sg_state,
                    pdf_url=None,
                    thumbnail_url=thumb_url,
                    source_page_url=target.url,
                    has_pdf=False,
                )
            )
        return out

    if state_match or "state" in section_tier.lower():
        award_tier = "State Award"
        award_category = heading_primary or award_category
        if remaining_texts:
            team_name = remaining_texts[0]
            if len(remaining_texts) > 1 and not location_raw:
                maybe_loc = remaining_texts[-1]
                if LOCATION_RE.match(maybe_loc):
                    location_raw = maybe_loc
                else:
                    project_title = " ".join(remaining_texts[1:])
        else:
            team_name = heading_primary or "Unknown Team"
    else:
        award_tier = section_tier or "Best in Show"
        team_name = heading_primary
        if remaining_texts:
            project_title = " ".join(remaining_texts)

    # If still no team_name, derive from PDF filename
    if not team_name and pdf_a:
        fname = pdf_a.rstrip("/").split("/")[-1].rsplit(".", 1)[0]
        team_name = re.sub(r"^\d+_\d+_", "", fname)
        team_name = re.sub(r"_\d{8,}$", "", team_name).replace("-", " ").replace("_", " ").strip()

    if not team_name:
        return []

    loc_city, loc_state = _parse_location(location_raw)
    if state_match and state_match.group(1) and not loc_state and len(state_match.group(1)) == 2:
        loc_state = state_match.group(1).upper()

    badge = f"{award_tier}: {award_category}" if award_category else award_tier
    report_id = make_report_id(target.slug, target.track, team_name, pdf_a)

    return [
        ManifestRecord(
            report_id=report_id,
            season=target.season,
            season_slug=target.slug,
            season_order=target.order,
            year=target.year,
            term=target.term,  # type: ignore[arg-type]
            track=target.track,  # type: ignore[arg-type]
            division=division,
            award_tier=award_tier,
            award_category=award_category,
            award_badges=[badge],
            team_name=team_name,
            project_title=project_title,
            location_raw=location_raw,
            location_city=loc_city,
            location_state=loc_state,
            pdf_url=pdf_a,
            thumbnail_url=thumb_url,
            source_page_url=target.url,
            has_pdf=bool(pdf_a),
        )
    ]


def parse_awards_html(html: str, target: SeasonTarget) -> list[ManifestRecord]:
    """Parse a single Plant the Moon awards HTML page into ManifestRecord objects."""
    soup = BeautifulSoup(html, "lxml")

    # Remove header/footer/nav noise if present
    for tag in soup.select("header, footer, nav"):
        tag.decompose()

    records: list[ManifestRecord] = []
    seen_pdfs: set[str] = set()
    current_tier = "Best in Show"

    # Walk document sections sequentially so State Award vs Best in Show context is preserved
    main_root = soup.find("main") or soup.body or soup
    for el in main_root.find_all(["h1", "h2", "h3", "div", "section"]):
        # Detect section headers
        if el.name in {"h1", "h2", "h3"}:
            htxt = _clean_text(el)
            low = htxt.lower()
            if "state award" in low:
                current_tier = "State Award"
            elif "space grant" in low:
                current_tier = "Space Grant Award"
            elif "best in show" in low and "winner" in low:
                current_tier = "Best in Show"
            elif "honorable mention" in low:
                current_tier = "Honorable Mention"
            elif "national" in low and "winner" in low:
                current_tier = "National Winner"
            continue

        # Leaf card columns (exclude outer layout columns that wrap inner sections/columns)
        classes = el.get("class") or []
        is_col = "elementor-column" in classes or "e-con" in classes
        if not is_col:
            continue
        if el.select_one(".elementor-column, .elementor-inner-section"):
            continue

        extracted = _extract_column_record(el, target, current_tier)
        for rec in extracted:
            if rec.pdf_url:
                seen_pdfs.add(rec.pdf_url)
            records.append(rec)

    # Safety fallback: guarantee every .pdf link in body is captured even on legacy 2021 DOMs
    for a in main_root.find_all("a", href=True):
        href = urljoin(target.url, a["href"].strip())
        if ".pdf" not in href.lower() or href in seen_pdfs:
            continue
        seen_pdfs.add(href)
        parent = a.find_parent(["div", "section", "li", "td", "article"]) or a.parent
        heading = parent.find(["h1", "h2", "h3", "h4", "strong"]) if parent else None
        team_name = _clean_text(heading) if heading else ""
        if not team_name or team_name.lower() in {"report", "best in show winners"}:
            fname = href.rstrip("/").split("/")[-1].rsplit(".", 1)[0]
            team_name = re.sub(r"^\d+_\d+_", "", fname).replace("-", " ").replace("_", " ").strip()
        division = "Elementary/Middle School" if target.track == "junior" else "High School / Professional"
        records.append(
            ManifestRecord(
                report_id=make_report_id(target.slug, target.track, team_name, href),
                season=target.season,
                season_slug=target.slug,
                season_order=target.order,
                year=target.year,
                term=target.term,  # type: ignore[arg-type]
                track=target.track,  # type: ignore[arg-type]
                division=division,
                award_tier="Best in Show",
                award_category=None,
                award_badges=["Best in Show"],
                team_name=team_name,
                project_title=None,
                pdf_url=href,
                source_page_url=target.url,
                has_pdf=True,
            )
        )

    return _deduplicate_records(records)


def _norm_team_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _deduplicate_records(records: list[ManifestRecord]) -> list[ManifestRecord]:
    """Merge duplicate team entries on the same page (e.g., Best in Show + State Winner)."""
    by_pdf: dict[str, ManifestRecord] = {}
    no_pdf: list[ManifestRecord] = []

    for rec in records:
        if rec.pdf_url:
            if rec.pdf_url in by_pdf:
                existing = by_pdf[rec.pdf_url]
                for b in rec.award_badges:
                    if b not in existing.award_badges:
                        existing.award_badges.append(b)
                if not existing.project_title and rec.project_title:
                    existing.project_title = rec.project_title
                if not existing.location_state and rec.location_state:
                    existing.location_raw = rec.location_raw
                    existing.location_city = rec.location_city
                    existing.location_state = rec.location_state
            else:
                by_pdf[rec.pdf_url] = rec
        else:
            no_pdf.append(rec)

    # Merge state-award metadata into matching PDF winner when team name matches within season/track
    pdf_by_team = {
        (r.season_slug, r.track, _norm_team_key(r.team_name)): r for r in by_pdf.values()
    }
    kept_no_pdf: list[ManifestRecord] = []
    for rec in no_pdf:
        key = (rec.season_slug, rec.track, _norm_team_key(rec.team_name))
        if key in pdf_by_team:
            target = pdf_by_team[key]
            for b in rec.award_badges:
                if b not in target.award_badges:
                    target.award_badges.append(b)
            if not target.location_state and rec.location_state:
                target.location_raw = rec.location_raw
                target.location_city = rec.location_city
                target.location_state = rec.location_state
        else:
            kept_no_pdf.append(rec)

    return list(by_pdf.values()) + kept_no_pdf


def scrape_archive(
    config_path: Path,
    pages_dir: Path,
    out_dir: Path,
    timeout: float = 25.0,
    from_cache: bool = False,
) -> list[ManifestRecord]:
    """Fetch all awards pages, save HTML snapshots, and export awards_index.{csv,json}."""
    targets, discover = load_season_targets(config_path)
    pages_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    existing_urls = {t.url for t in targets}
    all_records: list[ManifestRecord] = []

    headers = {
        "User-Agent": "CoSE-PTM-MetaAnalysis/0.1 (+https://github.com/dr-richard-barker/Plant_the_moon)"
    }
    with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
        idx = 0
        while idx < len(targets):
            target = targets[idx]
            idx += 1
            snap_path = pages_dir / f"{target.slug}_{target.track}.html"
            if from_cache and snap_path.exists():
                html = snap_path.read_text(encoding="utf-8")
            else:
                resp = client.get(target.url)
                resp.raise_for_status()
                html = resp.text
                snap_path.write_text(html, encoding="utf-8")

            if discover:
                extra = discover_extra_targets(html, existing_urls)
                targets.extend(extra)

            parsed = parse_awards_html(html, target)
            all_records.extend(parsed)

    # Global deduplication by PDF URL across pages if the same PDF is linked twice
    merged = _deduplicate_records(all_records)
    merged.sort(key=lambda r: (-r.season_order, r.track, not r.has_pdf, r.team_name.lower()))

    json_rows: list[dict[str, Any]] = [r.model_dump() for r in merged]
    (out_dir / "awards_index.json").write_text(json.dumps(json_rows, indent=2), encoding="utf-8")

    df = pd.DataFrame(json_rows)
    if not df.empty:
        df["award_badges"] = df["award_badges"].apply(lambda b: "; ".join(b) if isinstance(b, list) else "")
    df.to_csv(out_dir / "awards_index.csv", index=False)
    return merged
