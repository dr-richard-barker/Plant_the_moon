"""PDF text, layout, and table extraction using PyMuPDF and pdfplumber."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pdfplumber
import pymupdf

from ptm_meta.models import ManifestRecord


def _clean_page_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_single_pdf(rec: ManifestRecord, repo_root: Path, out_dir: Path, force: bool = False) -> dict[str, Any] | None:
    """Extract per-page text, embedded image counts, and tables from one PDF."""
    if not rec.has_pdf or not rec.local_pdf_path:
        return None

    out_path = out_dir / f"{rec.report_id}.json"
    if out_path.exists() and not force:
        return json.loads(out_path.read_text(encoding="utf-8"))

    pdf_path = repo_root / rec.local_pdf_path
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF file: {pdf_path}")

    pages: list[dict[str, Any]] = []
    total_chars = 0
    total_images = 0

    with pymupdf.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            txt = _clean_page_text(page.get_text("text"))
            n_imgs = len(page.get_images(full=False))
            total_chars += len(txt)
            total_images += n_imgs
            pages.append(
                {
                    "page_number": i,
                    "text": txt,
                    "char_count": len(txt),
                    "image_count": n_imgs,
                    "tables": [],
                }
            )

    # Extract tables cleanly with pdfplumber (capped at first 30 pages to prevent stalls)
    try:
        with pdfplumber.open(pdf_path) as plumber:
            for i, ppage in enumerate(plumber.pages[:30]):
                try:
                    raw_tables = ppage.extract_tables() or []
                except Exception:
                    raw_tables = []
                cleaned_tables = []
                for tbl in raw_tables[:8]:
                    rows = [
                        [re.sub(r"\s+", " ", cell or "").strip() for cell in row]
                        for row in tbl
                        if row and any((c or "").strip() for c in row)
                    ]
                    if rows:
                        cleaned_tables.append(rows[:40])
                if i < len(pages):
                    pages[i]["tables"] = cleaned_tables
    except Exception:
        pass

    n_pages = max(1, len(pages))
    avg_chars = total_chars / n_pages
    if avg_chars >= 150:
        quality = "digital_text"
    elif avg_chars >= 20:
        quality = "sparse_text"
    else:
        quality = "image_or_scanned"

    payload = {
        "report_id": rec.report_id,
        "sha256": rec.sha256,
        "page_count": len(pages),
        "total_chars": total_chars,
        "avg_chars_per_page": round(avg_chars, 1),
        "total_images": total_images,
        "table_count": sum(len(p["tables"]) for p in pages),
        "parse_quality": quality,
        "pages": pages,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def parse_all_pdfs(
    manifest_json: Path,
    repo_root: Path,
    out_dir: Path,
    force: bool = False,
) -> list[dict[str, Any]]:
    """Parse all fetched PDFs listed in manifest.json."""
    records = [
        ManifestRecord.model_validate(item)
        for item in json.loads(manifest_json.read_text(encoding="utf-8"))
    ]
    results: list[dict[str, Any]] = []
    for rec in records:
        parsed = parse_single_pdf(rec, repo_root=repo_root, out_dir=out_dir, force=force)
        if parsed is not None:
            results.append(parsed)
    return results
