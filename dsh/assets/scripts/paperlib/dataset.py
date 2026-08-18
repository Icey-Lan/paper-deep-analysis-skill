from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .common import read_json, write_text


def _statements(analysis: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for item in analysis["paper_narrative"].values():
        yield "narrative", item
    for item in analysis["contributions"]:
        yield "contribution", item
    method = analysis["method"]
    yield "method", method["problem"]
    yield "method", method["approach"]
    for item in method["workflow"]:
        yield "method", item
    for item in method["assumptions"]:
        yield "assumption", item
    synthesis = analysis["evidence_synthesis"]
    for key in ("strengths", "weaknesses", "reusability"):
        yield "finding", synthesis[key]
    assessment = analysis.get("evidence_assessment", {})
    for key in ("study_design", "datasets", "baselines", "metrics", "ablations", "negative_results"):
        item = assessment.get(key)
        if not isinstance(item, dict):
            continue
        record = dict(item)
        record.pop("status", None)
        record.pop("summary", None)
        record["id"] = f"assessment-{key.replace('_', '-')}"
        record["text"] = item.get("summary", "")
        # Adequacy judgments are the analyst's, not the authors'; the strength
        # mapping follows the status label the analyst chose.
        record["attribution"] = "analyst_inference"
        record["confidence"] = "medium"
        record["evidence_strength"] = {
            "adequate": "strong",
            "mixed": "moderate",
            "weak": "weak",
            "not_reported": "not_reported",
            "not_applicable": "not_reported",
        }.get(item.get("status"), "not_reported")
        record["tags"] = ["assessment", key.replace("_", "-")]
        yield "assessment", record
    for item in analysis["claims"]:
        yield "claim", item
    critical = analysis["critical_assessment"]
    for item in critical["strengths"]:
        yield "finding", item
    for item in critical["claim_evidence_gaps"]:
        yield "critique", item
    for item in critical["comparison_to_prior_work"]:
        yield "critique", item
    for item in critical["limitations"]:
        yield "limitation", item
    for item in critical["threats_to_validity"]:
        yield "limitation", item
    for item in critical["missing_evidence"]:
        yield "limitation", item
    yield "finding", critical["overall_judgment"]
    yield "reproducibility", analysis["reproducibility"]["replication_notes"]
    yield "profile_insight", analysis["profile_analysis"]["summary"]
    for item in analysis["profile_analysis"]["insights"]:
        yield "profile_insight", item
    for item in analysis["concepts"]:
        concept = dict(item)
        concept["text"] = (
            f"{item['term']}: {item['definition']} "
            f"Plain language: {item['plain_language']} Why it matters: {item['why_it_matters']}"
        )
        yield "concept", concept
    for item in analysis["open_questions"]:
        yield "open_question", item


def export_records(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    paper = analysis["paper"]
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for record_type, item in _statements(analysis):
        statement_id = item["id"]
        if statement_id in seen:
            raise ValueError(f"Duplicate statement id: {statement_id}")
        seen.add(statement_id)
        records.append(
            {
                "schema_version": "0.1.0",
                "record_id": f"{paper['stable_id']}:{statement_id}",
                "paper_id": paper["stable_id"],
                "paper_sha256": paper["identifiers"]["sha256"],
                "record_type": record_type,
                "statement": item["text"],
                "attribution": item["attribution"],
                "confidence": item["confidence"],
                "evidence_strength": item["evidence_strength"],
                "anchors": item["anchors"],
                "tags": item["tags"],
                "relations": [],
                "source": {"url": paper["source_url"], "license": paper["license"]},
            }
        )
    return records


def export_file(analysis_path: Path, output_path: Path) -> int:
    analysis = read_json(analysis_path)
    records = export_records(analysis)
    payload = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
    write_text(output_path, payload)
    return len(records)
