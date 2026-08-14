from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pypdf
from pypdf import PdfReader

from .common import write_json, write_text


class ExtractionError(RuntimeError):
    pass


def extract_pdf(
    pdf_path: Path,
    output_dir: Path,
    resolution: dict[str, Any],
    *,
    max_pages: int = 500,
    max_text_chars: int = 5_000_000,
) -> dict[str, Any]:
    try:
        document = PdfReader(str(pdf_path), strict=False)
    except Exception as exc:
        raise ExtractionError(f"PDF could not be opened: {exc}") from exc
    try:
        if document.is_encrypted:
            raise ExtractionError("Encrypted/password-protected PDFs are not supported.")
        page_count = len(document.pages)
        if page_count < 1:
            raise ExtractionError("PDF contains no pages.")
        if page_count > max_pages:
            raise ExtractionError(f"PDF has {page_count} pages, above the {max_pages}-page limit.")
        page_rows = []
        total_chars = 0
        warnings: list[str] = []
        for index, page in enumerate(document.pages):
            text = (page.extract_text() or "").strip()
            total_chars += len(text)
            if total_chars > max_text_chars:
                raise ExtractionError(f"Extracted text exceeds the {max_text_chars}-character limit.")
            page_rows.append({"page": index + 1, "chars": len(text), "text": text})
        minimum_text = max(500, page_count * 50)
        status = "ready" if total_chars >= minimum_text else "ocr_required"
        if status == "ocr_required":
            warnings.append(
                f"Only {total_chars} text characters were extracted from {page_count} pages; the PDF may be scanned or image-only."
            )
        if any(row["chars"] == 0 for row in page_rows):
            warnings.append("One or more pages yielded no extractable text.")
        pdf_meta = document.metadata or {}
        title = (resolution.get("title") or pdf_meta.get("/Title") or "").strip() or None
        authors = resolution.get("authors") or []
        if not authors and pdf_meta.get("/Author"):
            authors = [part.strip() for part in str(pdf_meta["/Author"]).split(";") if part.strip()]
        manifest = {
            "schema_version": "0.1.0",
            "status": status,
            "input_kind": resolution["input_kind"],
            "source_name": resolution["source_name"],
            "source_url": resolution["source_url"],
            "sha256": resolution["sha256"],
            "file_bytes": resolution["file_bytes"],
            "stable_id": resolution["stable_id"],
            "retrieved_at": resolution["retrieved_at"],
            "page_count": page_count,
            "text_chars": total_chars,
            "title": title,
            "authors": authors,
            "arxiv": resolution.get("arxiv"),
            "doi": resolution.get("doi"),
            "published": resolution.get("published"),
            "updated": resolution.get("updated"),
            "license": resolution.get("license") or "unknown",
            "extraction_engine": f"pypdf {pypdf.__version__}",
            "warnings": warnings,
        }
        lines = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in page_rows)
        write_text(output_dir / "pages.jsonl", lines)
        write_json(output_dir / "source-manifest.json", manifest)
        return manifest
    finally:
        del document
