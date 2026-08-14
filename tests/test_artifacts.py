from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import sample_analysis, sample_manifest, sample_run
from paperlib.common import write_json
from paperlib.dataset import export_file, export_records
from paperlib.render import render_file, render_report
from paperlib.validate import validate_all, validate_analysis, validate_dataset, validate_html, validate_run


def test_valid_analysis_matches_schema_and_manifest() -> None:
    errors, warnings, checks = validate_analysis(sample_analysis(), sample_manifest())
    assert errors == []
    assert "analysis-schema" in checks
    assert "source-identity" in checks


def test_manifest_hash_mismatch_fails() -> None:
    errors, _, _ = validate_analysis(sample_analysis(), sample_manifest("b" * 64))
    assert any("SHA-256" in error for error in errors)


def test_material_statement_requires_anchor() -> None:
    analysis = sample_analysis()
    analysis["claims"][0]["anchors"] = []
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("no evidence anchor" in error for error in errors)


def test_evidence_page_must_exist() -> None:
    analysis = sample_analysis()
    analysis["claims"][0]["anchors"][0]["page"] = 99
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("exceeds manifest page count" in error for error in errors)


def test_renderer_escapes_model_text() -> None:
    analysis = sample_analysis()
    analysis["executive_summary"]["one_sentence"] = '<script>alert("x")</script>'
    rendered = render_report(analysis)
    assert '<script>alert("x")</script>' not in rendered
    assert "&lt;script&gt;" in rendered


def test_html_is_offline_and_semantic(tmp_path: Path) -> None:
    analysis_path = tmp_path / "analysis.json"
    html_path = tmp_path / "report.html"
    write_json(analysis_path, sample_analysis())
    render_file(analysis_path, html_path)
    errors, _, checks = validate_html(html_path)
    assert errors == []
    assert "html-offline" in checks


def test_dataset_export_is_atomic_and_valid(tmp_path: Path) -> None:
    analysis_path = tmp_path / "analysis.json"
    dataset_path = tmp_path / "agent-learning.jsonl"
    write_json(analysis_path, sample_analysis())
    count = export_file(analysis_path, dataset_path)
    errors, _, checks = validate_dataset(dataset_path)
    assert count > 10
    assert errors == []
    assert "dataset-schema" in checks
    first = json.loads(dataset_path.read_text(encoding="utf-8").splitlines()[0])
    assert first["paper_sha256"] == "a" * 64
    assert first["source"]["license"] == "unknown"


def test_duplicate_statement_id_fails_dataset_export() -> None:
    analysis = sample_analysis()
    analysis["method"]["problem"]["id"] = analysis["contributions"][0]["id"]
    try:
        export_records(analysis)
    except ValueError as exc:
        assert "Duplicate statement id" in str(exc)
    else:
        raise AssertionError("duplicate id should fail")


def test_full_artifact_validation(tmp_path: Path) -> None:
    analysis_path = tmp_path / "analysis.json"
    manifest_path = tmp_path / "source-manifest.json"
    html_path = tmp_path / "report.html"
    dataset_path = tmp_path / "agent-learning.jsonl"
    run_path = tmp_path / "run.json"
    write_json(analysis_path, sample_analysis())
    write_json(manifest_path, sample_manifest())
    write_json(run_path, sample_run())
    render_file(analysis_path, html_path)
    export_file(analysis_path, dataset_path)
    result = validate_all(analysis_path, manifest_path=manifest_path, run_path=run_path, html_path=html_path, dataset_path=dataset_path)
    assert result["status"] == "pass"
    assert result["errors"] == []


def test_run_identity_mismatch_fails() -> None:
    run = sample_run()
    run["model"] = "different-model"
    errors, _, _ = validate_run(run, sample_analysis(), sample_manifest(), final_artifacts=True)
    assert any("model" in error for error in errors)


def test_pending_run_is_visible_before_finalization() -> None:
    run = sample_run()
    run["validation_status"] = "pending"
    errors, warnings, _ = validate_run(run, sample_analysis(), sample_manifest(), final_artifacts=True)
    assert errors == []
    assert any("pending" in warning for warning in warnings)


def test_cli_finalizes_run_only_after_artifacts_pass(tmp_path: Path) -> None:
    analysis_path = tmp_path / "analysis.json"
    manifest_path = tmp_path / "source-manifest.json"
    html_path = tmp_path / "report.html"
    dataset_path = tmp_path / "agent-learning.jsonl"
    run_path = tmp_path / "run.json"
    result_path = tmp_path / "validation.json"
    run = sample_run()
    run["validation_status"] = "pending"
    write_json(analysis_path, sample_analysis())
    write_json(manifest_path, sample_manifest())
    write_json(run_path, run)
    render_file(analysis_path, html_path)
    export_file(analysis_path, dataset_path)
    script = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "paper-deep-analysis" / "scripts" / "validate_artifacts.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--analysis", str(analysis_path),
            "--manifest", str(manifest_path),
            "--run", str(run_path),
            "--html", str(html_path),
            "--dataset", str(dataset_path),
            "--write-result", str(result_path),
            "--finalize-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(run_path.read_text(encoding="utf-8"))["validation_status"] == "pass"
    assert json.loads(result_path.read_text(encoding="utf-8"))["warnings"] == []


def test_unresolved_placeholder_fails() -> None:
    analysis = sample_analysis()
    analysis["executive_summary"]["bottom_line"] = "TODO"
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("placeholder" in error for error in errors)
