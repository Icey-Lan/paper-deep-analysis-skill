#!/usr/bin/env python3
"""Create the skill's self-contained runtime virtualenv.

The paper-deep-analysis skill's deterministic tooling needs Python 3.10+ with
`pypdf`, `requests`, and `jsonschema`. Instead of depending on (or mutating) the
host's Python environment — which on modern distros refuses bare `pip install`
under PEP 668 — this script creates a project-local virtualenv and installs the
pinned runtime dependencies into it.

It is idempotent: re-run it anytime `preflight` reports a missing dependency,
and it exits 0 immediately when the venv already satisfies the requirements.
On success it prints the virtualenv's Python binary, which the agent should use
for every skill command below (e.g. `.work/venv/bin/python` on POSIX,
`.work\\venv\\Scripts\\python.exe` on Windows).

Usage:
    python3 <skill-base-directory>/bootstrap.py --dir .work/venv
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
DEPENDENCIES = ("jsonschema>=4.21,<5", "pypdf>=5,<7", "requests>=2.31,<3")
REQUIRED_MODULES = ("jsonschema", "pypdf", "requests")


def venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def deps_ok(python: Path) -> bool:
    probe = (
        "import importlib.util, sys;"
        "mods = ('jsonschema', 'pypdf', 'requests');"
        "sys.exit(0 if all(importlib.util.find_spec(m) for m in mods) else 1)"
    )
    try:
        result = subprocess.run([str(python), "-c", probe], capture_output=True, timeout=120)
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def run(command: list[str], *, timeout: int, what: str) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, timeout=timeout)
    except subprocess.CalledProcessError as exc:
        detail = ""
        if exc.stderr:
            detail = exc.stderr.decode("utf-8", errors="replace")[-1200:]
        print(f"bootstrap: {what} failed:\n{detail}", file=sys.stderr)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the paper-deep-analysis skill runtime virtualenv.")
    parser.add_argument("--dir", type=Path, default=Path(".work") / "venv", help="virtualenv directory (default: .work/venv)")
    args = parser.parse_args()

    if sys.version_info < MIN_PYTHON:
        print(
            f"bootstrap: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required "
            f"(found {sys.version.split()[0]}).",
            file=sys.stderr,
        )
        return 2

    venv_dir = args.dir.resolve()
    python = venv_python(venv_dir)

    if python.is_file() and deps_ok(python):
        print(f"bootstrap: runtime venv already ready at {venv_dir}")
        print(python)
        return 0

    print(f"bootstrap: creating runtime venv at {venv_dir}")
    venv_dir.mkdir(parents=True, exist_ok=True)
    run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        timeout=300,
        what="virtualenv creation (on Debian/Ubuntu install python3-venv, e.g. apt install python3-venv, then retry)",
    )

    print("bootstrap: installing runtime dependencies (pypdf, requests, jsonschema)")
    run(
        [str(python), "-m", "pip", "install", "--disable-pip-version-check", *DEPENDENCIES],
        timeout=600,
        what="dependency install (check network access to PyPI and retry)",
    )

    if not deps_ok(python):
        print("bootstrap: dependencies still missing after install; inspect the output above.", file=sys.stderr)
        return 1

    print(f"bootstrap: ready. Use this Python for all skill commands:")
    print(python)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
