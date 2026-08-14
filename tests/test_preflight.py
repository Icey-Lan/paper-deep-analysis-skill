from __future__ import annotations

from pathlib import Path

from pypdf import PdfWriter

from paperlib.preflight import classify_input, run_preflight


def _pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with path.open("wb") as handle:
        writer.write(handle)


def test_preflight_local_pdf(tmp_path: Path) -> None:
    path = tmp_path / "paper.pdf"
    _pdf(path)
    result = run_preflight(str(path), tmp_path / "work")
    assert result["status"] == "pass"
    assert result["input_kind"] == "local_pdf"
    assert "local-input" in result["checks_passed"]


def test_preflight_unknown_input_fails(tmp_path: Path) -> None:
    result = run_preflight("missing-paper", tmp_path / "work")
    assert result["status"] == "fail"
    assert result["errors"][0]["code"] == "input.not_found"


def test_preflight_http_fails(tmp_path: Path) -> None:
    result = run_preflight("http://example.org/paper.pdf", tmp_path / "work")
    assert result["status"] == "fail"
    assert any(error["code"] == "network.scheme" for error in result["errors"])


def test_preflight_nonempty_output_fails(tmp_path: Path) -> None:
    output = tmp_path / "work"
    output.mkdir()
    (output / "existing.txt").write_text("keep", encoding="utf-8")
    result = run_preflight("2607.28033", output)
    assert result["status"] == "fail"
    assert any(error["code"] == "output.not_empty" for error in result["errors"])


def test_classify_inputs(tmp_path: Path) -> None:
    path = tmp_path / "paper.pdf"
    _pdf(path)
    assert classify_input(str(path)) == "local_pdf"
    assert classify_input("2607.28033") == "arxiv"
    assert classify_input("https://example.org/paper.pdf") == "public_url"
    assert classify_input("unknown") == "unknown"
