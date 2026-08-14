from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .common import contains_local_path, read_json, utc_now, write_json


SKILL_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_SCHEMA = SKILL_ROOT / "references" / "analysis.schema.json"
LEARNING_SCHEMA = SKILL_ROOT / "references" / "learning-record.schema.json"
RUN_SCHEMA = SKILL_ROOT / "references" / "run.schema.json"
MANIFEST_SCHEMA = SKILL_ROOT / "references" / "source-manifest.schema.json"
PLACEHOLDER_RE = re.compile(r"\b(?:replace[- ]with|not yet analyzed|todo|tbd)\b", re.IGNORECASE)
REVIEW_LEAD_RE = re.compile(
    r"^(?:这是一篇|这篇(?:论文|工作)(?:很|非常)?(?:有价值|优秀|重要|薄弱)|"
    r"this (?:is|paper is) (?:a )?(?:valuable|strong|weak|important))",
    re.IGNORECASE,
)
SUMMARY_FORMULA_RE = re.compile(
    r"(?:\$[^$]+\$|\\\(|\\\[|\b[OΘΩ]\s*\([^)]{1,48}\)|[α-ωΑ-Ω])"
)


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.counts: dict[str, int] = {}
        self.forbidden: list[str] = []
        self.remote_resources: list[str] = []
        self.ids: set[str] = set()
        self.href_fragments: list[str] = []
        self.has_skip_link = False
        self.has_print_css = False
        self.has_reading_progress = False
        self.has_current_section_css = False
        self.has_reduced_motion_css = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.counts[tag] = self.counts.get(tag, 0) + 1
        values = {key.lower(): value or "" for key, value in attrs}
        if "reading-progress" in values.get("class", "").split():
            self.has_reading_progress = True
        if tag in {"script", "iframe", "object", "embed", "svg"}:
            self.forbidden.append(tag)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("href", "").startswith("#"):
            self.href_fragments.append(values["href"][1:])
            if values["href"] == "#main" and "skip" in values.get("class", "").split():
                self.has_skip_link = True
        for attr in ("src", "srcset"):
            value = values.get(attr, "")
            if value.startswith(("http://", "https://", "//")):
                self.remote_resources.append(value)

    def handle_data(self, data: str) -> None:
        if "@media print" in data:
            self.has_print_css = True
        if "animation-timeline: --summary" in data and "view-timeline-name: --summary" in data:
            self.has_current_section_css = True
        if "@media (prefers-reduced-motion: reduce)" in data:
            self.has_reduced_motion_css = True


def _format_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{location}: {error.message}"


def _iter_statements(analysis: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any], bool]]:
    narrative = analysis.get("paper_narrative", {})
    for key in ("research_context", "prior_work_gap", "problem_importance", "proposed_solution", "main_findings"):
        if isinstance(narrative.get(key), dict):
            yield f"paper_narrative.{key}", narrative[key], True
    for index, item in enumerate(analysis.get("contributions", [])):
        yield f"contributions[{index}]", item, True
    method = analysis.get("method", {})
    for key in ("problem", "approach"):
        if isinstance(method.get(key), dict):
            yield f"method.{key}", method[key], True
    for key in ("workflow", "assumptions"):
        for index, item in enumerate(method.get(key, [])):
            yield f"method.{key}[{index}]", item, True
    synthesis = analysis.get("evidence_synthesis", {})
    for key in ("strengths", "weaknesses", "reusability"):
        if isinstance(synthesis.get(key), dict):
            yield f"evidence_synthesis.{key}", synthesis[key], True
    for index, item in enumerate(analysis.get("claims", [])):
        yield f"claims[{index}]", item, True
    critical = analysis.get("critical_assessment", {})
    for key in ("strengths", "claim_evidence_gaps", "comparison_to_prior_work", "limitations", "threats_to_validity", "missing_evidence"):
        for index, item in enumerate(critical.get(key, [])):
            yield f"critical_assessment.{key}[{index}]", item, True
    if isinstance(critical.get("overall_judgment"), dict):
        yield "critical_assessment.overall_judgment", critical["overall_judgment"], True
    reproduction = analysis.get("reproducibility", {})
    if isinstance(reproduction.get("replication_notes"), dict):
        yield "reproducibility.replication_notes", reproduction["replication_notes"], True
    profile = analysis.get("profile_analysis", {})
    if isinstance(profile.get("summary"), dict):
        yield "profile_analysis.summary", profile["summary"], True
    for index, item in enumerate(profile.get("insights", [])):
        yield f"profile_analysis.insights[{index}]", item, True
    for index, item in enumerate(analysis.get("concepts", [])):
        yield f"concepts[{index}]", item, True
    for index, item in enumerate(analysis.get("open_questions", [])):
        yield f"open_questions[{index}]", item, False


def validate_analysis(analysis: dict[str, Any], manifest: dict[str, Any] | None = None) -> tuple[list[str], list[str], list[str]]:
    schema = read_json(ANALYSIS_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [_format_error(error) for error in sorted(validator.iter_errors(analysis), key=lambda item: list(item.absolute_path))]
    warnings: list[str] = []
    checks = ["analysis-schema"] if not errors else []
    summary = analysis.get("executive_summary", {})
    core_conclusion = str(summary.get("core_conclusion", "")).strip()
    analyst_verdict = str(summary.get("analyst_verdict", "")).strip()
    language = str(analysis.get("analysis_context", {}).get("language", "")).lower()
    if REVIEW_LEAD_RE.search(core_conclusion):
        errors.append("executive_summary.core_conclusion begins with an analyst review instead of the paper's problem-method-finding logic")
    if core_conclusion and analyst_verdict and core_conclusion == analyst_verdict:
        errors.append("executive_summary.core_conclusion must remain distinct from analyst_verdict")
    if language.startswith("zh") and len(core_conclusion) > 220:
        errors.append("executive_summary.core_conclusion exceeds the 220-character Chinese readability limit")
    if SUMMARY_FORMULA_RE.search(core_conclusion):
        errors.append("executive_summary.core_conclusion contains formula notation; explain the result in plain language and move formulas to the method or evidence sections")
    if errors:
        return errors, warnings, checks

    serialized = json.dumps(analysis, ensure_ascii=False)
    if contains_local_path(serialized):
        errors.append("analysis contains a local absolute path")
    if PLACEHOLDER_RE.search(serialized):
        errors.append("analysis contains an unresolved template placeholder")
    if analysis["analysis_context"]["profile"] != analysis["profile_analysis"]["profile"]:
        errors.append("analysis_context.profile does not match profile_analysis.profile")
    seen: set[str] = set()
    page_count = manifest.get("page_count") if manifest else None
    for index, item in enumerate(analysis.get("key_metrics", [])):
        location = f"key_metrics[{index}]"
        item_id = item.get("id")
        if item_id in seen:
            errors.append(f"{location}: duplicate item id {item_id}")
        seen.add(item_id)
        anchors = item.get("anchors", [])
        if not anchors:
            errors.append(f"{location}: key metric has no evidence anchor")
        for anchor in anchors:
            page = anchor.get("page")
            if page_count and page and page > page_count:
                errors.append(f"{location}: evidence page {page} exceeds manifest page count {page_count}")
    for index, item in enumerate(analysis.get("evidence_synthesis", {}).get("experiments", [])):
        location = f"evidence_synthesis.experiments[{index}]"
        for anchor in item.get("anchors", []):
            page = anchor.get("page")
            if page_count and page and page > page_count:
                errors.append(f"{location}: evidence page {page} exceeds manifest page count {page_count}")
    for location, item, anchor_required in _iter_statements(analysis):
        item_id = item.get("id")
        if item_id in seen:
            errors.append(f"{location}: duplicate statement id {item_id}")
        seen.add(item_id)
        anchors = item.get("anchors", [])
        if anchor_required and not anchors:
            errors.append(f"{location}: material statement has no evidence anchor")
        for anchor in anchors:
            page = anchor.get("page")
            if page_count and page and page > page_count:
                errors.append(f"{location}: evidence page {page} exceeds manifest page count {page_count}")
        if (
            item.get("attribution") == "paper_claim"
            and item.get("evidence_strength") == "not_reported"
            and item.get("confidence") == "high"
        ):
            warnings.append(f"{location}: a high-confidence paper claim is paired with not_reported evidence")
    if analysis["analysis_boundary"]["basis"] == "abstract_only":
        warnings.append("analysis declares abstract_only; do not present it as a full-paper deep read")
    if manifest:
        if analysis["paper"]["identifiers"]["sha256"] != manifest.get("sha256"):
            errors.append("paper SHA-256 does not match source manifest")
        if analysis["paper"]["stable_id"] != manifest.get("stable_id"):
            errors.append("paper stable_id does not match source manifest")
        if manifest.get("status") != "ready":
            errors.append(f"source manifest is not ready: {manifest.get('status', 'unknown')}")
    if not errors:
        checks.extend(["analysis-semantics", "source-identity"] if manifest else ["analysis-semantics"])
    return errors, warnings, checks


def validate_manifest(manifest: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    validator = Draft202012Validator(read_json(MANIFEST_SCHEMA), format_checker=FormatChecker())
    errors = [_format_error(error) for error in validator.iter_errors(manifest)]
    serialized = json.dumps(manifest, ensure_ascii=False)
    if contains_local_path(serialized):
        errors.append("source manifest contains a local absolute path")
    if manifest.get("input_kind") == "local_pdf" and manifest.get("source_name") != "local-paper.pdf":
        errors.append("local-PDF source_name must be redacted to local-paper.pdf")
    source_url = manifest.get("source_url") or ""
    if "?" in source_url or "#" in source_url:
        errors.append("source manifest URL contains a query string or fragment")
    return errors, [], ["manifest-schema", "manifest-public-safety"] if not errors else []


def validate_run(
    run: dict[str, Any],
    analysis: dict[str, Any],
    manifest: dict[str, Any] | None,
    *,
    final_artifacts: bool,
) -> tuple[list[str], list[str], list[str]]:
    validator = Draft202012Validator(read_json(RUN_SCHEMA), format_checker=FormatChecker())
    errors = [_format_error(error) for error in validator.iter_errors(run)]
    warnings: list[str] = []
    serialized = json.dumps(run, ensure_ascii=False)
    if contains_local_path(serialized):
        errors.append("run record contains a local absolute path")
    if PLACEHOLDER_RE.search(serialized):
        errors.append("run record contains an unresolved placeholder")
    boundary = analysis.get("analysis_boundary", {})
    context = analysis.get("analysis_context", {})
    if run.get("host") != boundary.get("host"):
        errors.append("run.host does not match analysis boundary host")
    if run.get("model") != boundary.get("model"):
        errors.append("run.model does not match analysis boundary model")
    if run.get("analysis_basis") != boundary.get("basis"):
        errors.append("run.analysis_basis does not match analysis boundary basis")
    if run.get("profile") != context.get("profile"):
        errors.append("run.profile does not match analysis context profile")
    if manifest:
        if run.get("source_sha256") != manifest.get("sha256"):
            errors.append("run.source_sha256 does not match source manifest")
        if run.get("input_kind") != manifest.get("input_kind"):
            errors.append("run.input_kind does not match source manifest")
    if final_artifacts and run.get("validation_status") == "fail":
        errors.append("run.validation_status is fail")
    elif run.get("validation_status") == "pending":
        warnings.append("run validation status is still pending")
    return errors, warnings, ["run-schema", "run-identity", "run-public-safety"] if not errors else []


def validate_html(path: Path) -> tuple[list[str], list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    parser = ReportParser()
    parser.feed(text)
    errors: list[str] = []
    warnings: list[str] = []
    if parser.counts.get("main", 0) != 1:
        errors.append("HTML must contain exactly one main element")
    if parser.counts.get("h1", 0) != 1:
        errors.append("HTML must contain exactly one h1 element")
    if parser.forbidden:
        errors.append(f"HTML contains forbidden active/embedded tags: {sorted(set(parser.forbidden))}")
    if parser.remote_resources:
        errors.append("HTML loads remote resources and is not self-contained")
    if not parser.has_skip_link:
        errors.append("HTML is missing a skip link to main content")
    if not parser.has_print_css:
        errors.append("HTML is missing print styles")
    if not parser.has_reading_progress:
        errors.append("HTML is missing the reading progress indicator")
    if not parser.has_current_section_css:
        errors.append("HTML is missing CSS current-section table-of-contents feedback")
    if not parser.has_reduced_motion_css:
        errors.append("HTML is missing reduced-motion styles")
    if parser.counts.get("figure", 0) < 1:
        errors.append("HTML must contain at least one captioned explanatory figure")
    if parser.counts.get("figcaption", 0) != parser.counts.get("figure", 0):
        errors.append("Every HTML figure must have a figcaption")
    if parser.counts.get("meter", 0):
        errors.append("HTML contains an unexplained meter-style evidence score")
    if parser.counts.get("table", 0) < 1:
        errors.append("HTML is missing the compact experiment evidence table")
    missing_fragments = sorted({fragment for fragment in parser.href_fragments if fragment and fragment not in parser.ids})
    if missing_fragments:
        errors.append(f"HTML has unresolved fragment links: {missing_fragments}")
    if contains_local_path(text):
        errors.append("HTML contains a local absolute path")
    if PLACEHOLDER_RE.search(text):
        errors.append("HTML contains an unresolved template placeholder")
    if '<html lang="zh' in text and any(token in text for token in ("Reading boundary", "Analysis basis:", "Generation disclosure", "Source locations:")):
        errors.append("Chinese HTML contains untranslated interface copy")
    return errors, warnings, ["html-structure", "html-offline", "html-public-safety"] if not errors else []


def validate_dataset(path: Path) -> tuple[list[str], list[str], list[str]]:
    schema = read_json(LEARNING_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    warnings: list[str] = []
    record_ids: set[str] = set()
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            count += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"dataset line {line_number}: invalid JSON: {exc}")
                continue
            for error in validator.iter_errors(record):
                errors.append(f"dataset line {line_number}: {_format_error(error)}")
            record_id = record.get("record_id") if isinstance(record, dict) else None
            if record_id in record_ids:
                errors.append(f"dataset line {line_number}: duplicate record_id {record_id}")
            if record_id:
                record_ids.add(record_id)
            serialized = json.dumps(record, ensure_ascii=False)
            if contains_local_path(serialized):
                errors.append(f"dataset line {line_number}: contains a local absolute path")
            if PLACEHOLDER_RE.search(serialized):
                errors.append(f"dataset line {line_number}: contains an unresolved placeholder")
    if count == 0:
        errors.append("dataset contains no records")
    return errors, warnings, ["dataset-schema", "dataset-identity", "dataset-public-safety"] if not errors else []


def validate_all(
    analysis_path: Path,
    *,
    manifest_path: Path | None = None,
    run_path: Path | None = None,
    html_path: Path | None = None,
    dataset_path: Path | None = None,
) -> dict[str, Any]:
    analysis = read_json(analysis_path)
    manifest = read_json(manifest_path) if manifest_path else None
    errors, warnings, checks = validate_analysis(analysis, manifest)
    if manifest:
        new_errors, new_warnings, new_checks = validate_manifest(manifest)
        errors.extend(new_errors)
        warnings.extend(new_warnings)
        checks.extend(new_checks)
    if run_path:
        new_errors, new_warnings, new_checks = validate_run(
            read_json(run_path),
            analysis,
            manifest,
            final_artifacts=bool(html_path or dataset_path),
        )
        errors.extend(new_errors)
        warnings.extend(new_warnings)
        checks.extend(new_checks)
    if html_path:
        new_errors, new_warnings, new_checks = validate_html(html_path)
        errors.extend(new_errors)
        warnings.extend(new_warnings)
        checks.extend(new_checks)
    if dataset_path:
        new_errors, new_warnings, new_checks = validate_dataset(dataset_path)
        errors.extend(new_errors)
        warnings.extend(new_warnings)
        checks.extend(new_checks)
    return {
        "schema_version": "0.1.0",
        "validated_at": utc_now(),
        "status": "pass" if not errors else "fail",
        "checks_passed": sorted(set(checks)),
        "errors": errors,
        "warnings": warnings,
    }


def validate_and_write(
    analysis_path: Path,
    *,
    manifest_path: Path | None = None,
    run_path: Path | None = None,
    html_path: Path | None = None,
    dataset_path: Path | None = None,
    result_path: Path | None = None,
) -> dict[str, Any]:
    result = validate_all(
        analysis_path,
        manifest_path=manifest_path,
        run_path=run_path,
        html_path=html_path,
        dataset_path=dataset_path,
    )
    if result_path:
        write_json(result_path, result)
    return result
