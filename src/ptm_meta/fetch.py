"""Polite PDF downloader with SHA-256 provenance verification and page count inspection."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
import pymupdf

from ptm_meta.models import ManifestRecord


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _pdf_page_count(path: Path) -> int | None:
    try:
        with pymupdf.open(path) as doc:
            return len(doc)
    except Exception:
        return None


def _download_one(
    rec: ManifestRecord,
    pdfs_root: Path,
    repo_root: Path,
    verify_only: bool,
    timeout: float,
) -> ManifestRecord:
    if not rec.has_pdf or not rec.pdf_url:
        return rec

    dest = pdfs_root / rec.season_slug / rec.track / f"{rec.report_id}.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    rel_path = str(dest.relative_to(repo_root))

    if dest.exists() and dest.stat().st_size > 0:
        digest = _sha256_file(dest)
        if verify_only and rec.sha256 and rec.sha256 != digest:
            raise ValueError(f"SHA-256 mismatch for {rel_path}: {digest} != {rec.sha256}")
        return rec.model_copy(
            update={
                "local_pdf_path": rel_path,
                "sha256": digest,
                "byte_size": dest.stat().st_size,
                "page_count": _pdf_page_count(dest),
                "http_status": rec.http_status or 200,
                "fetched_at_utc": rec.fetched_at_utc or datetime.now(timezone.utc).isoformat(),
            }
        )

    headers = {
        "User-Agent": "CoSE-PTM-MetaAnalysis/0.1 (+https://github.com/dr-richard-barker/Plant_the_moon)"
    }
    tmp_dest = dest.with_suffix(".pdf.part")
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
                with client.stream("GET", rec.pdf_url) as resp:
                    status = resp.status_code
                    resp.raise_for_status()
                    with tmp_dest.open("wb") as f:
                        for chunk in resp.iter_bytes():
                            f.write(chunk)
            tmp_dest.replace(dest)
            digest = _sha256_file(dest)
            return rec.model_copy(
                update={
                    "local_pdf_path": rel_path,
                    "sha256": digest,
                    "byte_size": dest.stat().st_size,
                    "page_count": _pdf_page_count(dest),
                    "http_status": status,
                    "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception as exc:
            last_err = exc
            if tmp_dest.exists():
                tmp_dest.unlink()
            if attempt == 2:
                break

    return rec.model_copy(
        update={
            "local_pdf_path": None,
            "http_status": getattr(getattr(last_err, "response", None), "status_code", None),
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )


def fetch_pdfs(
    index_json_path: Path,
    pdfs_root: Path,
    repo_root: Path,
    manifest_dir: Path,
    verify_only: bool = False,
    max_workers: int = 6,
    timeout: float = 60.0,
) -> list[ManifestRecord]:
    """Download all PDFs in awards_index.json and write manifest.{json,csv}."""
    raw_items = json.loads(index_json_path.read_text(encoding="utf-8"))
    records = [ManifestRecord.model_validate(item) for item in raw_items]

    updated: list[ManifestRecord] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_download_one, rec, pdfs_root, repo_root, verify_only, timeout): idx
            for idx, rec in enumerate(records)
        }
        ordered: dict[int, ManifestRecord] = {}
        for fut in as_completed(futures):
            idx = futures[fut]
            ordered[idx] = fut.result()
        updated = [ordered[i] for i in range(len(records))]

    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_rows: list[dict[str, Any]] = [r.model_dump() for r in updated]
    (manifest_dir / "manifest.json").write_text(json.dumps(json_rows, indent=2), encoding="utf-8")

    df = pd.DataFrame(json_rows)
    if not df.empty:
        df["award_badges"] = df["award_badges"].apply(lambda b: "; ".join(b) if isinstance(b, list) else "")
    df.to_csv(manifest_dir / "manifest.csv", index=False)
    return updated
