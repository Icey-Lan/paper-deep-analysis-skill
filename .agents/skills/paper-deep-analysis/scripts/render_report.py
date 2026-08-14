#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from paperlib.render import render_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a self-contained paper analysis HTML report.")
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    render_file(args.analysis, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
