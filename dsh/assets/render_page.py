#!/usr/bin/env python3
"""Render source-PDF pages to PNG so an image-capable host model can inspect
figures, tables, diagrams, and equations.

The paper-deep-analysis skill's text extraction cannot see visuals. When key
evidence is visual, render the relevant pages of the prepared source PDF and
view the PNGs with the host's image tool (in DeepSeek Harness: `read_image`).

`pymupdf` is an optional dependency: install it into the skill's runtime venv
once when first needed (the script prints the exact command), then re-run. It is
deliberately not part of the base runtime so ordinary runs do not pay for it.

Usage:
    <venv-python> <skill-base>/render_page.py \
        --pdf .work/<RUN_ID>/source.pdf --page 4 --page 12 \
        --output-dir .work/<RUN_ID>/figures [--dpi 150]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import pymupdf  # PyMuPDF >= 1.24 preferred module name
except ImportError:  # pragma: no cover - older PyMuPDF exposes the fitz name
    try:
        import fitz as pymupdf  # type: ignore
    except ImportError:
        pymupdf = None  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG for visual inspection.")
    parser.add_argument("--pdf", required=True, type=Path, help="the prepared source PDF")
    parser.add_argument("--page", required=True, type=int, action="append", help="1-based page number; repeatable")
    parser.add_argument("--output-dir", required=True, type=Path, help="directory for the rendered PNGs")
    parser.add_argument("--dpi", type=int, default=150, help="render resolution (default 150)")
    args = parser.parse_args()

    if pymupdf is None:
        print(
            "render_page: pymupdf is not installed in the runtime environment.\n"
            f"Install it once and re-run: {sys.executable} -m pip install pymupdf",
            file=sys.stderr,
        )
        return 3

    pdf_path = args.pdf.resolve()
    if not pdf_path.is_file():
        print(f"render_page: PDF not found: {pdf_path}", file=sys.stderr)
        return 2
    if not 72 <= args.dpi <= 400:
        print("render_page: --dpi must be between 72 and 400", file=sys.stderr)
        return 2

    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open(str(pdf_path))
    try:
        page_count = len(document)
        scale = args.dpi / 72.0
        for number in args.page:
            if number < 1 or number > page_count:
                print(f"render_page: page {number} is out of range (1..{page_count})", file=sys.stderr)
                return 2
            pix = document[number - 1].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
            out = out_dir / f"page-{number:03d}.png"
            pix.save(str(out))
            print(out)
    finally:
        document.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
