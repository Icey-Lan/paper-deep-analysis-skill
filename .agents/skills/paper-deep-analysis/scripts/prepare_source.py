#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from paperlib.extract import ExtractionError, extract_pdf
from paperlib.source import DEFAULT_MAX_BYTES, SourceError, resolve_source


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Safely resolve and extract a paper PDF.")
    value.add_argument("input", help="Local PDF, public PDF/landing URL, arXiv ID, or arXiv URL")
    value.add_argument("--output-dir", required=True, type=Path, help="New or empty local work directory")
    value.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    value.add_argument("--max-pages", type=int, default=500)
    value.add_argument("--max-text-chars", type=int, default=5_000_000)
    value.add_argument("--allow-http", action="store_true", help="Permit public HTTP URLs (unsafe default override)")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        pdf_path, resolution = resolve_source(
            args.input,
            args.output_dir,
            max_bytes=args.max_bytes,
            allow_http=args.allow_http,
        )
        manifest = extract_pdf(
            pdf_path,
            args.output_dir,
            resolution,
            max_pages=args.max_pages,
            max_text_chars=args.max_text_chars,
        )
    except (SourceError, ExtractionError, OSError) as exc:
        print(f"prepare_source: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if manifest["status"] != "ready":
        print("prepare_source: OCR or a different text-bearing PDF is required.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
