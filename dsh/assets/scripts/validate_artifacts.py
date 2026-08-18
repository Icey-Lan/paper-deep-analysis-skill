#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paperlib.common import read_json, write_json
from paperlib.validate import validate_and_write


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate analysis, provenance, HTML, and Agent dataset artifacts.")
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--write-result", type=Path)
    parser.add_argument(
        "--finalize-run",
        action="store_true",
        help="After every check passes, atomically mark run.validation_status as pass and validate again.",
    )
    args = parser.parse_args()
    result = validate_and_write(
        args.analysis,
        manifest_path=args.manifest,
        run_path=args.run,
        html_path=args.html,
        dataset_path=args.dataset,
        result_path=args.write_result,
    )
    if args.finalize_run:
        if not args.run:
            parser.error("--finalize-run requires --run")
        if result["status"] == "pass":
            run = read_json(args.run)
            run["validation_status"] = "pass"
            write_json(args.run, run)
            result = validate_and_write(
                args.analysis,
                manifest_path=args.manifest,
                run_path=args.run,
                html_path=args.html,
                dataset_path=args.dataset,
                result_path=args.write_result,
            )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
