#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paperlib.common import write_json
from paperlib.preflight import run_preflight
from paperlib.input_guard import DEFAULT_MAX_BYTES


def main() -> int:
    parser = argparse.ArgumentParser(description="Check runtime, input, network target, and output safety before a paper run.")
    parser.add_argument("input")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--check-network", action="store_true")
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = run_preflight(args.input, args.output_dir, max_bytes=args.max_bytes, check_network=args.check_network)
    if args.write_result:
        write_json(args.write_result, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
