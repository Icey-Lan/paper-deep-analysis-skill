from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from paperlib.extract import ExtractionError, extract_pdf
from paperlib.source import SourceError, fetch_bytes, guard_url, parse_arxiv_id, resolve_source


class FakeResponse:
    def __init__(self, data: bytes = b"", *, status: int = 200, content_type: str = "application/pdf", url: str = "https://example.org/paper.pdf", location: str | None = None) -> None:
        self._data = data
        self.status_code = status
        self.url = url
        self.headers = {"Content-Type": content_type, "Content-Length": str(len(data))}
        if location:
            self.headers["Location"] = location

    def iter_content(self, chunk_size: int):
        yield from (self._data[index:index + chunk_size] for index in range(0, len(self._data), chunk_size))

    def close(self) -> None:
        return None


class FakeSession:
    def __init__(self, handler) -> None:
        self.handler = handler
        self.calls: list[str] = []

    def get(self, url: str, **kwargs):
        self.calls.append(url)
        return self.handler(url)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2607.28033", "2607.28033"),
        ("2607.28033v2", "2607.28033v2"),
        ("https://arxiv.org/abs/2607.28033", "2607.28033"),
        ("https://arxiv.org/pdf/2607.28033.pdf", "2607.28033"),
        ("hep-th/9901001", "hep-th/9901001"),
        ("not-an-id", None),
    ],
)
def test_parse_arxiv_id(value: str, expected: str | None) -> None:
    assert parse_arxiv_id(value) == expected


def test_guard_url_refuses_http_before_dns() -> None:
    with pytest.raises(SourceError, match="HTTPS"):
        guard_url("http://example.org/paper.pdf")


def test_guard_url_refuses_credentials() -> None:
    with pytest.raises(SourceError, match="credentials"):
        guard_url("https://user:secret@example.org/paper.pdf")


def test_guard_url_refuses_private_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))])
    with pytest.raises(SourceError, match="non-public"):
        guard_url("https://example.org/paper.pdf")


def test_guard_url_accepts_global_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))])
    guard_url("https://example.org/paper.pdf")


def _write_text_pdf(path: Path, text: str = "Evidence " * 200) -> None:
    document = canvas.Canvas(str(path))
    for index in range(0, len(text), 90):
        document.drawString(50, 800 - (index // 90) * 14, text[index:index + 90])
    document.save()


def _text_pdf_bytes() -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    document = canvas.Canvas(buffer)
    text = "Evidence " * 200
    for index in range(0, len(text), 90):
        document.drawString(50, 800 - (index // 90) * 14, text[index:index + 90])
    document.save()
    return buffer.getvalue()


def _global_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))])


def test_fetch_validates_redirect_target(monkeypatch: pytest.MonkeyPatch) -> None:
    def dns(host: str, *args, **kwargs):
        address = "127.0.0.1" if host == "private.example" else "93.184.216.34"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]

    monkeypatch.setattr(socket, "getaddrinfo", dns)
    session = FakeSession(lambda url: FakeResponse(status=302, url=url, location="https://private.example/secret.pdf"))
    with pytest.raises(SourceError, match="non-public"):
        fetch_bytes("https://example.org/paper", max_bytes=1024, session=session)
    assert session.calls == ["https://example.org/paper"]


def test_direct_public_pdf_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _global_dns(monkeypatch)
    pdf = _text_pdf_bytes()
    session = FakeSession(lambda url: FakeResponse(pdf, url="https://cdn.example.org/paper.pdf?token=secret"))
    path, resolution = resolve_source("https://example.org/paper.pdf", tmp_path / "work", session=session)
    assert path.read_bytes() == pdf
    assert resolution["input_kind"] == "public_url"
    assert resolution["source_name"] == "remote-paper.pdf"
    assert resolution["stable_id"] == f"paper-{resolution['sha256'][:12]}"
    assert resolution["source_url"] == "https://cdn.example.org/paper.pdf"
    assert "secret" not in json.dumps(resolution)


def test_landing_page_discovers_citation_pdf(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _global_dns(monkeypatch)
    pdf = _text_pdf_bytes()
    html = b'<html><head><meta name="citation_pdf_url" content="/download/paper.pdf"></head></html>'

    def handler(url: str) -> FakeResponse:
        if url.endswith("/paper"):
            return FakeResponse(html, content_type="text/html", url=url)
        return FakeResponse(pdf, url=url)

    session = FakeSession(handler)
    _, resolution = resolve_source("https://example.org/paper", tmp_path / "work", session=session)
    assert resolution["input_kind"] == "landing_page"
    assert session.calls == ["https://example.org/paper", "https://example.org/download/paper.pdf"]


def test_ambiguous_landing_page_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _global_dns(monkeypatch)
    html = b'<a href="a.pdf">A</a><a href="b.pdf">B</a>'
    session = FakeSession(lambda url: FakeResponse(html, content_type="text/html", url=url))
    with pytest.raises(SourceError, match="ambiguous"):
        resolve_source("https://example.org/paper", tmp_path / "work", session=session)


def test_landing_page_without_pdf_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _global_dns(monkeypatch)
    html = b"<html><body><h1>Abstract only</h1></body></html>"
    session = FakeSession(lambda url: FakeResponse(html, content_type="text/html", url=url))
    with pytest.raises(SourceError, match="no explicit public PDF"):
        resolve_source("https://example.org/paper", tmp_path / "work", session=session)


def test_arxiv_resolution_parses_metadata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _global_dns(monkeypatch)
    pdf = _text_pdf_bytes()
    atom = b'''<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
      <entry><title>Fixture Paper</title><author><name>Ada Researcher</name></author>
      <published>2026-01-02T00:00:00Z</published><updated>2026-01-03T00:00:00Z</updated>
      <arxiv:doi>10.1000/fixture</arxiv:doi><link title="license" href="https://creativecommons.org/licenses/by/4.0/"/></entry>
    </feed>'''

    def handler(url: str) -> FakeResponse:
        if "api/query" in url:
            return FakeResponse(atom, content_type="application/atom+xml", url=url)
        return FakeResponse(pdf, url=url)

    _, resolution = resolve_source("2607.28033", tmp_path / "work", session=FakeSession(handler))
    assert resolution["arxiv"] == "2607.28033"
    assert resolution["title"] == "Fixture Paper"
    assert resolution["authors"] == ["Ada Researcher"]
    assert resolution["doi"] == "10.1000/fixture"
    assert resolution["license"].startswith("https://creativecommons.org/")


def test_local_pdf_preparation_redacts_original_path(tmp_path: Path) -> None:
    original = tmp_path / "private-name.pdf"
    work = tmp_path / "work"
    _write_text_pdf(original)
    pdf_path, resolution = resolve_source(str(original), work)
    manifest = extract_pdf(pdf_path, work, resolution)
    serialized = json.dumps(manifest)
    assert manifest["status"] == "ready"
    assert manifest["source_name"] == "local-paper.pdf"
    assert manifest["stable_id"] == f"paper-{manifest['sha256'][:12]}"
    assert str(tmp_path) not in serialized
    assert "private-name.pdf" not in serialized
    assert (work / "pages.jsonl").is_file()


def test_scanned_pdf_is_detected(tmp_path: Path) -> None:
    original = tmp_path / "blank.pdf"
    work = tmp_path / "work"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with original.open("wb") as handle:
        writer.write(handle)
    pdf_path, resolution = resolve_source(str(original), work)
    manifest = extract_pdf(pdf_path, work, resolution)
    assert manifest["status"] == "ocr_required"
    assert manifest["warnings"]


def test_encrypted_pdf_is_refused(tmp_path: Path) -> None:
    original = tmp_path / "encrypted.pdf"
    work = tmp_path / "work"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("fixture-password")
    with original.open("wb") as handle:
        writer.write(handle)
    pdf_path, resolution = resolve_source(str(original), work)
    with pytest.raises(ExtractionError, match="Encrypted"):
        extract_pdf(pdf_path, work, resolution)


def test_page_limit_is_enforced(tmp_path: Path) -> None:
    original = tmp_path / "two-pages.pdf"
    work = tmp_path / "work"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    with original.open("wb") as handle:
        writer.write(handle)
    pdf_path, resolution = resolve_source(str(original), work)
    with pytest.raises(ExtractionError, match="page limit"):
        extract_pdf(pdf_path, work, resolution, max_pages=1)


def test_text_limit_is_enforced(tmp_path: Path) -> None:
    original = tmp_path / "text.pdf"
    work = tmp_path / "work"
    _write_text_pdf(original)
    pdf_path, resolution = resolve_source(str(original), work)
    with pytest.raises(ExtractionError, match="character limit"):
        extract_pdf(pdf_path, work, resolution, max_text_chars=100)


def test_local_file_size_limit(tmp_path: Path) -> None:
    original = tmp_path / "large.pdf"
    original.write_bytes(b"%PDF-" + b"x" * 20)
    with pytest.raises(SourceError, match="limit"):
        resolve_source(str(original), tmp_path / "work", max_bytes=10)


def test_malformed_pdf_fails_extraction(tmp_path: Path) -> None:
    original = tmp_path / "bad.pdf"
    original.write_bytes(b"%PDF-this-is-not-a-real-pdf")
    work = tmp_path / "work"
    pdf_path, resolution = resolve_source(str(original), work)
    with pytest.raises(ExtractionError, match="could not be opened"):
        extract_pdf(pdf_path, work, resolution)
