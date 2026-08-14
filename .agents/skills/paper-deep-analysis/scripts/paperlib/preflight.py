from __future__ import annotations

import importlib.metadata
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .common import utc_now
from .input_guard import DEFAULT_MAX_BYTES, InputGuardError, guard_url, parse_arxiv_id


REQUIRED_FILES = (
    "SKILL.md",
    "references/analysis.schema.json",
    "references/learning-record.schema.json",
    "references/run.schema.json",
    "references/source-manifest.schema.json",
    "assets/analysis-template.json",
    "assets/run-template.json",
)
DEPENDENCIES = ("pypdf", "requests", "jsonschema")


def classify_input(value: str) -> str:
    local = Path(value).expanduser()
    if local.is_file():
        return "local_pdf"
    if parse_arxiv_id(value):
        return "arxiv"
    if urlsplit(value).scheme:
        return "public_url"
    return "unknown"


def _existing_parent(path: Path) -> Path:
    candidate = path.resolve()
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate


def run_preflight(
    value: str,
    output_dir: Path,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    check_network: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    checks: list[str] = []
    kind = classify_input(value)
    skill_root = Path(__file__).resolve().parents[2]

    if sys.version_info < (3, 10):
        errors.append({"code": "runtime.python", "message": "Python 3.10 or newer is required."})
    else:
        checks.append("python-version")
    for dependency in DEPENDENCIES:
        try:
            importlib.metadata.version(dependency)
        except importlib.metadata.PackageNotFoundError:
            errors.append({"code": "runtime.dependency", "message": f"Missing dependency: {dependency}."})
    if not any(item["code"] == "runtime.dependency" for item in errors):
        checks.append("dependencies")
    missing = [relative for relative in REQUIRED_FILES if not (skill_root / relative).is_file()]
    if missing:
        errors.append({"code": "runtime.skill_files", "message": f"Missing required Skill files: {', '.join(missing)}"})
    else:
        checks.append("skill-files")

    if kind == "unknown":
        errors.append({"code": "input.not_found", "message": "Input is not an existing PDF, supported arXiv ID, or URL."})
    elif kind == "local_pdf":
        local = Path(value).expanduser()
        if local.suffix.lower() != ".pdf":
            errors.append({"code": "input.not_pdf", "message": "Local input must use the .pdf extension."})
        elif local.stat().st_size > max_bytes:
            errors.append({"code": "limit.bytes", "message": f"Local PDF exceeds the {max_bytes}-byte limit."})
        else:
            checks.append("local-input")
    elif kind == "public_url":
        parts = urlsplit(value)
        if parts.scheme.lower() != "https":
            errors.append({"code": "network.scheme", "message": "Remote inputs require HTTPS."})
        elif parts.username or parts.password:
            errors.append({"code": "network.credentials", "message": "URLs containing credentials are not allowed."})
        elif check_network:
            try:
                guard_url(value)
                checks.append("network-target")
            except InputGuardError as exc:
                code = "network.private" if "non-public" in str(exc) else "network.target"
                errors.append({"code": code, "message": str(exc)})
        else:
            warnings.append({"code": "network.not_checked", "message": "DNS/network target was not checked during preflight; preparation will check it."})
    else:
        if check_network:
            try:
                guard_url("https://export.arxiv.org/")
                guard_url("https://arxiv.org/")
                checks.append("network-target")
            except InputGuardError as exc:
                errors.append({"code": "network.target", "message": str(exc)})

    if output_dir.exists() and any(output_dir.iterdir()):
        errors.append({"code": "output.not_empty", "message": "Output directory exists and is not empty."})
    else:
        parent = _existing_parent(output_dir)
        if not os.access(parent, os.W_OK):
            errors.append({"code": "output.not_writable", "message": "Output directory parent is not writable."})
        else:
            checks.append("output-target")
    return {
        "schema_version": "0.1.0",
        "checked_at": utc_now(),
        "status": "pass" if not errors else "fail",
        "input_kind": kind,
        "checks_passed": checks,
        "errors": errors,
        "warnings": warnings,
    }
