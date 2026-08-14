from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "paper-deep-analysis"


def test_skill_frontmatter_and_name() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    assert metadata["name"] == SKILL.name
    assert len(metadata["name"]) <= 64
    assert len(metadata["description"]) <= 1024
    assert "local PDF" in metadata["description"]
    assert "arXiv" in metadata["description"]
    assert len(body.splitlines()) < 500
    assert ".agents/skills/paper-deep-analysis/scripts" not in body
    assert "PAPER_SKILL_DIR" in body


def test_eval_set_covers_inputs_failures_and_negative_routes() -> None:
    evals = json.loads((SKILL / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
    identifiers = {item["id"] for item in evals}
    assert {1, 2, 3, 4, 5, 6, 7, 8} == identifiers
    assert all(item.get("expected_output") for item in evals)
    assert all(item.get("expectations") for item in evals)
    assert any(item["expected_route"].startswith("not-") for item in evals)
