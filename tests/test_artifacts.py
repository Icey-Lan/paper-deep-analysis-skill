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
    analysis["executive_summary"]["core_conclusion"] = '<script>alert("x")</script>' * 4
    rendered = render_report(analysis)
    assert '<script>alert("x")</script>' not in rendered
    assert "&lt;script&gt;" in rendered


def test_renderer_preserves_dense_visual_contract() -> None:
    rendered = render_report(sample_analysis())
    assert rendered.count("<figure") >= 2
    assert "reading-progress" in rendered
    assert "<meter" not in rendered
    assert 'class="metrics-strip metrics-columns-' in rendered
    assert 'class="process-flow"' in rendered
    assert 'class="evidence-table"' in rendered
    assert 'id="narrative"' in rendered
    assert 'id="concepts"' in rendered
    assert "animation-timeline: --summary" in rendered
    assert "view-timeline-name: --critique" in rendered
    assert sample_analysis()["executive_summary"]["headline"] in rendered.split("<h1>", 1)[1].split("</h1>", 1)[0]
    assert "Paper source" in rendered
    assert 'href="https://example.org/test-paper.pdf"' in rendered


def test_executive_summary_leads_with_paper_logic_not_review_verdict() -> None:
    analysis = sample_analysis()
    rendered = render_report(analysis)
    summary_html = rendered.split('id="summary"', 1)[1].split("</section>", 1)[0]
    assert analysis["executive_summary"]["core_conclusion"] in summary_html
    assert summary_html.index(analysis["executive_summary"]["core_conclusion"]) < summary_html.index(analysis["executive_summary"]["analyst_verdict"])


def test_review_style_core_conclusion_is_rejected() -> None:
    analysis = sample_analysis()
    analysis["executive_summary"]["core_conclusion"] = "This is a valuable paper, but the evidence remains scoped and the broader deployment claim still needs independent verification."
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("begins with an analyst review" in error for error in errors)


def test_chinese_core_conclusion_readability_limits_are_enforced() -> None:
    analysis = sample_analysis()
    analysis["analysis_context"]["language"] = "zh-CN"
    analysis["executive_summary"]["core_conclusion"] = "这篇论文研究一个重要问题，并提出清晰的方法来完成验证。" * 10
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("220-character Chinese readability limit" in error for error in errors)


def test_formula_notation_is_rejected_in_core_conclusion() -> None:
    analysis = sample_analysis()
    analysis["executive_summary"]["core_conclusion"] = "The paper reduces the cumulative cost from O(n²) to O(n) while retaining the stated evaluation result."
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("contains formula notation" in error for error in errors)


def test_key_metric_strip_hides_citations_and_chinese_ui_is_localized() -> None:
    analysis = sample_analysis()
    analysis["analysis_context"]["language"] = "zh-CN"
    rendered = render_report(analysis)
    metric_strip = rendered.split('class="metrics-strip ', 1)[1].split("</figure>", 1)[0]
    assert 'class="source-line"' not in metric_strip
    assert "阅读依据" in rendered
    assert "判断来源" in rendered
    assert "生成说明" in rendered
    assert "Reading boundary" not in rendered


def test_dense_metric_strip_caps_desktop_grid_at_three_columns() -> None:
    analysis = sample_analysis()
    analysis["key_metrics"] = [dict(analysis["key_metrics"][0], id=f"metric-{index}") for index in range(6)]
    rendered = render_report(analysis)
    assert 'class="metrics-strip metrics-columns-3"' in rendered
    assert "--metric-columns:3" in rendered
    assert "repeat(var(--metric-count)" not in rendered


def test_narrative_label_and_copy_share_top_alignment() -> None:
    rendered = render_report(sample_analysis())
    assert ".narrative-block { display: grid; grid-template-columns: 8.5rem minmax(0,1fr); align-items: start;" in rendered
    assert ".narrative-block h3 { margin: 0;" in rendered


def test_dynamic_memory_profile_is_schema_valid() -> None:
    analysis = sample_analysis()
    analysis["analysis_context"]["profile"] = "memory"
    analysis["profile_analysis"]["profile"] = "memory"
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert errors == []


def test_run_schema_accepts_every_analysis_profile() -> None:
    profiles = [
        "general", "agent-systems", "agent-evaluation", "harness", "memory",
        "continual-learning", "multi-agent", "tool-use", "reasoning-planning",
        "data-agent", "embodied-agent", "custom",
    ]
    for profile in profiles:
        analysis = sample_analysis()
        analysis["analysis_context"]["profile"] = profile
        analysis["profile_analysis"]["profile"] = profile
        run = sample_run()
        run["profile"] = profile
        errors, _, _ = validate_run(run, analysis, sample_manifest(), final_artifacts=False)
        assert errors == [], f"{profile}: {errors}"


def test_unexplained_meter_is_rejected(tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    rendered = render_report(sample_analysis()).replace("</main>", '<meter min="0" max="3" value="2">2</meter></main>')
    html_path.write_text(rendered, encoding="utf-8")
    errors, _, _ = validate_html(html_path)
    assert any("unexplained meter" in error for error in errors)


def test_missing_current_section_feedback_is_rejected(tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    rendered = render_report(sample_analysis()).replace("animation-timeline: --summary", "animation-timeline: none")
    html_path.write_text(rendered, encoding="utf-8")
    errors, _, _ = validate_html(html_path)
    assert any("current-section" in error for error in errors)


def test_citations_are_grouped_after_reading_units() -> None:
    rendered = render_report(sample_analysis())
    statement_count = len(list(rendered.split('class="source-line"'))) - 1
    assert statement_count < 20
    assert sample_analysis()["executive_summary"]["evidence_summary"] in rendered


def test_key_metric_requires_valid_anchor() -> None:
    analysis = sample_analysis()
    analysis["key_metrics"][0]["anchors"] = []
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("key_metrics" in error and "non-empty" in error for error in errors)


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
    analysis["executive_summary"]["analyst_verdict"] = "TODO: replace with a calibrated analyst verdict."
    errors, _, _ = validate_analysis(analysis, sample_manifest())
    assert any("placeholder" in error for error in errors)
