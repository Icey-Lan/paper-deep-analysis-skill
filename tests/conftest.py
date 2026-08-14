from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPTS = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "paper-deep-analysis" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def anchor(page: int = 1, section: str = "1 Introduction") -> dict[str, Any]:
    return {"page": page, "section": section, "figure": None, "table": None, "note": "fixture evidence"}


def statement(identifier: str, text: str, *, attribution: str = "paper_claim", evidence: str = "moderate") -> dict[str, Any]:
    return {
        "id": identifier,
        "text": text,
        "attribution": attribution,
        "confidence": "medium",
        "evidence_strength": evidence,
        "anchors": [anchor()],
        "tags": ["fixture"],
    }


def sample_analysis(sha256: str = "a" * 64) -> dict[str, Any]:
    claim = statement("claim-main", "The reported experiment supports the primary claim.")
    claim.update({"claim_type": "empirical", "support": "The main table reports a controlled comparison."})
    return {
        "schema_version": "0.1.0",
        "paper": {
            "stable_id": "test-paper",
            "title": "A Test Paper",
            "authors": ["Ada Researcher", "Lin Engineer"],
            "identifiers": {"arxiv": None, "doi": None, "sha256": sha256},
            "source_url": "https://example.org/test-paper.pdf",
            "published": "2026-01-02",
            "updated": None,
            "license": "unknown",
            "venue": None,
        },
        "analysis_context": {
            "language": "en",
            "profile": "general",
            "reader_context": "Technical reader",
            "focus_questions": ["Is the main claim supported?"],
        },
        "analysis_boundary": {
            "basis": "full_text",
            "model": "test-model",
            "host": "test-host",
            "visuals_inspected": ["Table 1"],
            "extraction_warnings": [],
        },
        "executive_summary": {
            "one_sentence": "The paper tests a bounded research method.",
            "why_it_matters": "It exposes a reusable evaluation pattern.",
            "bottom_line": "The evidence is useful but scoped.",
        },
        "contributions": [statement("contribution-main", "The paper defines a concrete method.")],
        "method": {
            "problem": statement("method-problem", "The target problem is under-specified evaluation."),
            "approach": statement("method-approach", "The method combines two controlled stages."),
            "workflow": [statement("method-step-one", "Stage one prepares the inputs.")],
            "assumptions": [statement("assumption-data", "The data represents the target setting.", attribution="analyst_inference")],
        },
        "evidence_assessment": {
            key: {"status": "mixed", "summary": f"{key} is present with a limitation.", "anchors": [anchor()]}
            for key in ("study_design", "datasets", "baselines", "metrics", "ablations", "negative_results")
        },
        "claims": [claim],
        "critical_assessment": {
            "strengths": [statement("strength-design", "The comparison is easy to inspect.", attribution="analyst_inference")],
            "limitations": [statement("limitation-scope", "The evaluation covers one setting.")],
            "threats_to_validity": [statement("threat-selection", "Selection effects may limit transfer.", attribution="analyst_inference")],
            "missing_evidence": [statement("missing-cost", "Operational cost is not reported.", evidence="not_reported")],
            "overall_judgment": statement("judgment-overall", "The method is promising within the reported scope.", attribution="analyst_inference"),
        },
        "reproducibility": {
            "code": "not_reported",
            "data": "not_reported",
            "environment": "partial",
            "replication_notes": statement("reproduction-note", "A replication needs the missing configuration.", attribution="derived_lesson"),
        },
        "profile_analysis": {
            "profile": "general",
            "insights": [statement("profile-insight", "The evaluation pattern may transfer to similar studies.", attribution="derived_lesson")],
        },
        "open_questions": [statement("question-scale", "Does the result hold at larger scale?", attribution="derived_lesson", evidence="not_reported")],
        "references": [{"label": "Paper", "url": "https://example.org/test-paper.pdf", "kind": "paper"}],
    }


def sample_manifest(sha256: str = "a" * 64) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "status": "ready",
        "input_kind": "local_pdf",
        "source_name": "local-paper.pdf",
        "source_url": None,
        "sha256": sha256,
        "file_bytes": 1024,
        "stable_id": "test-paper",
        "retrieved_at": "2026-08-14T00:00:00+00:00",
        "page_count": 3,
        "text_chars": 3000,
        "title": "A Test Paper",
        "authors": ["Ada Researcher"],
        "arxiv": None,
        "doi": None,
        "published": None,
        "updated": None,
        "license": "unknown",
        "extraction_engine": "fixture",
        "warnings": [],
    }


def sample_run(sha256: str = "a" * 64) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "run_id": "fixture-run",
        "created_at": "2026-08-14T00:00:00+00:00",
        "host": "test-host",
        "model": "test-model",
        "external_model_api_used": False,
        "analysis_basis": "full_text",
        "profile": "general",
        "input_kind": "local_pdf",
        "source_sha256": sha256,
        "validation_status": "pass",
        "warnings": [],
    }
