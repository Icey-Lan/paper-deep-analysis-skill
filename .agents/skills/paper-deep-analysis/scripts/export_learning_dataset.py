#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from paperlib.dataset import export_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Export atomic Agent-learning records from analysis JSON.")
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    count = export_file(args.analysis, args.output)
    print(f"{args.output} ({count} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
