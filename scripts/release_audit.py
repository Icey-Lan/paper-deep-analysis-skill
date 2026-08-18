#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SKILL = ROOT / ".agents" / "skills" / "paper-deep-analysis"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "paper-deep-analysis"
MAX_PUBLIC_FILE_BYTES = 2 * 1024 * 1024
BLOCKED_NAMES = {"source.pdf", "pages.jsonl", ".env", ".env.local"}
BLOCKED_SUFFIXES = {".pdf", ".p12", ".pfx", ".key", ".pem", ".zip"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".html", ".yml", ".yaml", ".toml", ".txt"}
SECRET_PATTERNS = {
    "OpenAI key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "URL credentials": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@", re.IGNORECASE),
}
LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/[^/\s]+/"),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    re.compile(r"file://", re.IGNORECASE),
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
LOCAL_PATTERN_DEFINITION_FILES = {
    Path("scripts/release_audit.py"),
    Path(".agents/skills/paper-deep-analysis/scripts/paperlib/common.py"),
    # The dsh bundle ships a byte-identical copy of the canonical paperlib.
    Path("dsh/assets/scripts/paperlib/common.py"),
}


def candidate_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(ROOT / item.decode() for item in result.stdout.split(b"\0") if item)


def check_markdown_links(path: Path, text: str) -> list[str]:
    errors = []
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {raw_target}")
    return errors


def audit() -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if not CLAUDE_SKILL.is_symlink():
        errors.append(".claude/skills/paper-deep-analysis must be a symlink to the canonical Skill")
    elif CLAUDE_SKILL.resolve() != CANONICAL_SKILL.resolve():
        errors.append("Claude Code Skill entry does not resolve to the canonical .agents Skill")
    files = candidate_files()
    for path in files:
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            target = path.resolve()
            if ROOT not in target.parents:
                errors.append(f"{relative}: symlink points outside the repository")
            continue
        if not path.is_file():
            continue
        if path.name in BLOCKED_NAMES or path.suffix.lower() in BLOCKED_SUFFIXES:
            errors.append(f"{relative}: blocked source/binary file type")
        size = path.stat().st_size
        if size > MAX_PUBLIC_FILE_BYTES:
            errors.append(f"{relative}: file exceeds {MAX_PUBLIC_FILE_BYTES} bytes")
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative}: expected UTF-8 text")
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if relative == Path("tests/test_source.py") and label == "URL credentials":
                continue
            if pattern.search(text):
                errors.append(f"{relative}: possible {label}")
        if relative not in LOCAL_PATTERN_DEFINITION_FILES and any(pattern.search(text) for pattern in LOCAL_PATH_PATTERNS):
            errors.append(f"{relative}: contains a local absolute path or file URL")
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON: {exc}")
        if path.suffix.lower() == ".jsonl":
            for line_number, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"{relative}:{line_number}: invalid JSONL: {exc}")
        if path.suffix.lower() == ".md":
            errors.extend(check_markdown_links(path, text))
    if not files:
        warnings.append("No candidate files were found.")
    return {
        "status": "pass" if not errors else "fail",
        "files_checked": len(files),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
