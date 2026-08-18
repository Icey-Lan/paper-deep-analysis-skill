#!/usr/bin/env python3
"""Sync or verify the shared skill resources between the canonical source and
the DSH plugin bundle (dsh/assets/).

The DSH plugin ships its own copies of `references/`, `scripts/`, and `assets/`
so it installs as a self-contained bundle. The canonical source of truth remains
`.agents/skills/paper-deep-analysis/`.

Modes:
  sync    Copy the three shared directories deterministically from canonical
          into dsh/assets/ (default).
  --check Verify dsh/assets/ matches canonical byte-for-byte and that every
          file the bundled preflight step requires is present. Exit non-zero on
          drift. Intended for CI and the release gate.

`dsh/assets/SKILL.md` and any other DSH-only files at the top level of
`dsh/assets/` are intentionally NOT copied or checked against canonical.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

SHARED_SUBDIRS = ("references", "scripts", "assets")


def _dircmp_recurse(left: Path, right: Path) -> list[str]:
    """Byte-level drift report between two directories (relative paths)."""
    diffs: list[str] = []
    comparison = filecmp.dircmp(left, right)
    for name in comparison.left_only:
        diffs.append(f"only in canonical: {name}")
    for name in comparison.right_only:
        diffs.append(f"only in dsh/assets: {name}")
    for name in comparison.diff_files:
        diffs.append(f"content differs: {name}")
    for name in comparison.funny_files:
        diffs.append(f"uncomparable: {name}")
    for name in comparison.common_dirs:
        diffs.extend(_dircmp_recurse(left / name, right / name))
    return diffs


def run_sync(dsh_dir: Path, canonical: Path, dest: Path) -> int:
    if not (canonical / "SKILL.md").is_file():
        print(f"sync-assets: canonical SKILL.md not found at {canonical}", file=sys.stderr)
        return 1
    for subdir in SHARED_SUBDIRS:
        src = canonical / subdir
        dst = dest / subdir
        if not src.is_dir():
            print(f"sync-assets: canonical {subdir} missing at {src}", file=sys.stderr)
            return 1
        if dst.exists() or dst.is_symlink():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"sync-assets: copied {subdir} -> {dst}")
    return check_required(dest)


def check_required(dest: Path) -> int:
    required = (
        "references/analysis.schema.json",
        "references/learning-record.schema.json",
        "references/run.schema.json",
        "references/source-manifest.schema.json",
        "assets/analysis-template.json",
        "assets/run-template.json",
    )
    missing = [rel for rel in required if not (dest / rel).is_file()]
    if missing:
        print("sync-assets: missing required files: " + ", ".join(missing), file=sys.stderr)
        return 1
    return 0


def run_check(dsh_dir: Path, canonical: Path, dest: Path) -> int:
    ok = True
    if not (canonical / "SKILL.md").is_file():
        print("sync-assets: canonical SKILL.md not found", file=sys.stderr)
        return 1
    for subdir in SHARED_SUBDIRS:
        src = canonical / subdir
        dst = dest / subdir
        if not src.is_dir():
            print(f"sync-assets: canonical {subdir} missing", file=sys.stderr)
            return 1
        if not dst.is_dir():
            print(f"sync-assets: dsh/assets/{subdir} missing (run sync-assets.py)", file=sys.stderr)
            ok = False
            continue
        diffs = _dircmp_recurse(src, dst)
        if diffs:
            ok = False
            print(f"sync-assets: drift in {subdir}/", file=sys.stderr)
            for line in diffs:
                print(f"  - {line}", file=sys.stderr)
    if check_required(dest) != 0:
        ok = False
    if ok:
        print("sync-assets: dsh/assets is in sync with canonical")
        return 0
    print("sync-assets: run `python dsh/sync-assets.py` to resync", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync or check dsh/assets against the canonical skill.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify dsh/assets matches canonical byte-for-byte; do not modify files",
    )
    args = parser.parse_args()
    dsh_dir = Path(__file__).resolve().parent
    repo_root = dsh_dir.parent
    canonical = repo_root / ".agents" / "skills" / "paper-deep-analysis"
    dest = dsh_dir / "assets"
    if args.check:
        return run_check(dsh_dir, canonical, dest)
    return run_sync(dsh_dir, canonical, dest)


if __name__ == "__main__":
    raise SystemExit(main())
