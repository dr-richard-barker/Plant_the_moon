"""Command-line interface for the FAIR Plant the Moon meta-analysis pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from ptm_meta.extract import extract_all
from ptm_meta.fair import build_ro_crate, validate_fair_artifacts
from ptm_meta.fetch import fetch_pdfs
from ptm_meta.manuscript import compile_manuscript_pdf
from ptm_meta.normalize import normalize_and_export
from ptm_meta.pdf_parse import parse_all_pdfs
from ptm_meta.scrape import scrape_archive

console = Console()


def _repo_root(arg_root: str | None) -> Path:
    return Path(arg_root).resolve() if arg_root else Path.cwd().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ptm-meta",
        description="FAIR ingestion, AI/ML meta-analysis, and CoSE publishing CLI.",
    )
    parser.add_argument("--root", default=None, help="Repository root directory (defaults to CWD).")

    sub = parser.add_subparsers(dest="cmd", required=True)
    p_scrape = sub.add_parser("scrape", help="Scrape awards pages and save HTML snapshots + awards_index.")
    p_scrape.add_argument("--from-cache", action="store_true", help="Re-parse cached HTML pages.")

    p_fetch = sub.add_parser("fetch", help="Download PDFs and build SHA-256 manifest.")
    p_fetch.add_argument("--verify", action="store_true", help="Verify SHA-256 of existing PDFs.")
    p_fetch.add_argument("--workers", type=int, default=6)

    p_parse = sub.add_parser("parse", help="Extract text and tables from PDFs.")
    p_parse.add_argument("--force", action="store_true")

    p_ext = sub.add_parser("extract", help="Run structured extraction (Gemini or heuristic).")
    p_ext.add_argument("--backend", choices=["auto", "gemini", "heuristic"], default="auto")
    p_ext.add_argument("--model", default="gemini-2.5-flash")
    p_ext.add_argument("--limit", type=int, default=None)
    p_ext.add_argument("--force", action="store_true")

    sub.add_parser("normalize", help="Normalize extractions and export FAIR CSV/Parquet/JSON.")
    sub.add_parser("build-manuscript", help="Compile Typst synthesis manuscript PDF.")
    sub.add_parser("build-fair", help="Generate ro-crate-metadata.json and validate schemas.")
    sub.add_parser("validate-fair", help="Validate existing manifest, extractions, and RO-Crate.")

    p_all = sub.add_parser("all", help="Run full pipeline end-to-end.")
    p_all.add_argument("--backend", choices=["auto", "gemini", "heuristic"], default="auto")
    p_all.add_argument("--model", default="gemini-2.5-flash")
    p_all.add_argument("--limit", type=int, default=None)

    args = parser.parse_args(argv)
    root = _repo_root(args.root)

    cfg = root / "configs/seasons.yaml"
    pages_dir = root / "data/raw/pages"
    raw_dir = root / "data/raw"
    pdfs_dir = root / "data/raw/pdfs"
    parsed_dir = root / "data/interim/parsed_text"
    ext_dir = root / "data/interim/llm_extractions"
    processed_dir = root / "data/processed"
    static_data_dir = root / "book/_static/data"

    if args.cmd in ("scrape", "all"):
        recs = scrape_archive(
            cfg,
            pages_dir=pages_dir,
            out_dir=raw_dir,
            from_cache=getattr(args, "from_cache", False),
        )
        console.print(f"[bold teal]scrape[/]: indexed {len(recs)} records ({sum(r.has_pdf for r in recs)} PDFs).")

    if args.cmd in ("fetch", "all"):
        verify = getattr(args, "verify", False)
        workers = getattr(args, "workers", 6)
        recs = fetch_pdfs(
            raw_dir / "awards_index.json",
            pdfs_root=pdfs_dir,
            repo_root=root,
            manifest_dir=raw_dir,
            verify_only=verify,
            max_workers=workers,
        )
        ok = sum(1 for r in recs if r.sha256)
        console.print(f"[bold teal]fetch[/]: verified {ok}/{sum(r.has_pdf for r in recs)} PDFs with SHA-256.")

    if args.cmd in ("parse", "all"):
        parsed = parse_all_pdfs(
            raw_dir / "manifest.json",
            repo_root=root,
            out_dir=parsed_dir,
            force=getattr(args, "force", False),
        )
        console.print(f"[bold teal]parse[/]: parsed {len(parsed)} PDFs into {parsed_dir}.")

    if args.cmd in ("extract", "all"):
        ext = extract_all(
            raw_dir / "manifest.json",
            parsed_dir=parsed_dir,
            out_dir=ext_dir,
            repo_root=root,
            backend=args.backend,
            model_name=args.model,
            limit=args.limit,
            force=getattr(args, "force", False),
        )
        console.print(f"[bold teal]extract[/]: produced {len(ext)} structured extractions.")

    if args.cmd in ("normalize", "all"):
        df_r, df_a = normalize_and_export(
            raw_dir / "manifest.json",
            parsed_dir=parsed_dir,
            extractions_dir=ext_dir,
            processed_dir=processed_dir,
            static_data_dir=static_data_dir,
        )
        console.print(f"[bold teal]normalize[/]: exported {len(df_r)} reports & {len(df_a)} trial arms.")

    if args.cmd == "build-manuscript":
        pdf_out = compile_manuscript_pdf(root)
        console.print(f"[bold teal]manuscript[/]: compiled {pdf_out}.")

    if args.cmd in ("build-fair", "all"):
        crate = build_ro_crate(root)
        rep = validate_fair_artifacts(root)
        console.print(f"[bold green]FAIR[/]: built {crate.name} and validated {rep}.")

    if args.cmd == "validate-fair":
        rep = validate_fair_artifacts(root)
        console.print(f"[bold green]validate-fair[/]: {rep}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
