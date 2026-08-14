from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

import requests

from .common import public_url, sha256_file, stable_slug, utc_now, write_json
from .input_guard import DEFAULT_MAX_BYTES, InputGuardError, guard_url, parse_arxiv_id


MAX_REDIRECTS = 5
DEFAULT_MAX_HTML_BYTES = 2 * 1024 * 1024
USER_AGENT = "paper-deep-analysis-skill/0.1"


SourceError = InputGuardError


@dataclass(frozen=True)
class FetchResult:
    data: bytes
    url: str
    content_type: str


class PdfLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.citation_pdf_urls: list[str] = []
        self.pdf_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "meta" and values.get("name", "").lower() == "citation_pdf_url":
            if values.get("content"):
                self.citation_pdf_urls.append(values["content"])
        if tag.lower() == "a" and values.get("href"):
            href = values["href"]
            if href.lower().split("?", 1)[0].endswith(".pdf") or values.get("type", "").lower() == "application/pdf":
                self.pdf_links.append(href)


def fetch_bytes(
    url: str,
    *,
    max_bytes: int,
    allow_http: bool = False,
    session: requests.Session | None = None,
) -> FetchResult:
    client = session or requests.Session()
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        guard_url(current, allow_http=allow_http)
        try:
            response = client.get(
                current,
                headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,text/html,application/atom+xml"},
                stream=True,
                allow_redirects=False,
                timeout=(10, 60),
            )
        except requests.RequestException as exc:
            raise SourceError(f"Source request failed: {exc}") from exc
        if response.status_code in {301, 302, 303, 307, 308}:
            target = response.headers.get("Location")
            response.close()
            if not target:
                raise SourceError("Source redirect did not include a Location header.")
            current = urljoin(current, target)
            continue
        if response.status_code != 200:
            response.close()
            raise SourceError(f"Source returned HTTP {response.status_code}.")
        declared = response.headers.get("Content-Length")
        if declared and declared.isdigit() and int(declared) > max_bytes:
            response.close()
            raise SourceError(f"Source exceeds the {max_bytes}-byte limit.")
        chunks: list[bytes] = []
        size = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            size += len(chunk)
            if size > max_bytes:
                response.close()
                raise SourceError(f"Source exceeds the {max_bytes}-byte limit.")
            chunks.append(chunk)
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        final_url = response.url or current
        response.close()
        return FetchResult(b"".join(chunks), final_url, content_type)
    raise SourceError(f"Source exceeded the {MAX_REDIRECTS}-redirect limit.")


def _looks_like_pdf(data: bytes, content_type: str) -> bool:
    return data.lstrip().startswith(b"%PDF-") or content_type == "application/pdf"


def _discover_pdf_url(html_bytes: bytes, base_url: str) -> str:
    parser = PdfLinkParser()
    try:
        parser.feed(html_bytes.decode("utf-8", errors="replace"))
    except Exception as exc:
        raise SourceError("Could not parse the paper landing page safely.") from exc
    candidates = parser.citation_pdf_urls or parser.pdf_links
    normalized: list[str] = []
    for candidate in candidates:
        resolved = urljoin(base_url, candidate)
        if resolved not in normalized:
            normalized.append(resolved)
    if not normalized:
        raise SourceError("Landing page exposes no explicit public PDF link; provide an authorized local PDF.")
    if len(normalized) > 1 and not parser.citation_pdf_urls:
        raise SourceError("Landing page exposes multiple ambiguous PDF links; provide the intended PDF URL.")
    return normalized[0]


def _parse_arxiv_atom(data: bytes, arxiv_id: str) -> dict[str, Any]:
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        raise SourceError("arXiv metadata response was not valid Atom XML.") from exc
    entry = root.find("atom:entry", ns)
    if entry is None:
        return {"arxiv": arxiv_id, "title": None, "authors": [], "published": None, "updated": None, "doi": None, "license": "unknown"}

    def text(path: str) -> str | None:
        node = entry.find(path, ns)
        return " ".join(node.text.split()) if node is not None and node.text else None

    authors = []
    for author in entry.findall("atom:author", ns):
        name = author.find("atom:name", ns)
        if name is not None and name.text:
            authors.append(" ".join(name.text.split()))
    license_url = "unknown"
    for link in entry.findall("atom:link", ns):
        if link.attrib.get("title") == "license" and link.attrib.get("href"):
            license_url = link.attrib["href"]
            break
    return {
        "arxiv": arxiv_id,
        "title": text("atom:title"),
        "authors": authors,
        "published": (text("atom:published") or "")[:10] or None,
        "updated": (text("atom:updated") or "")[:10] or None,
        "doi": text("arxiv:doi"),
        "license": license_url,
    }


def resolve_source(
    value: str,
    output_dir: Path,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    allow_http: bool = False,
    session: requests.Session | None = None,
) -> tuple[Path, dict[str, Any]]:
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SourceError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "source.pdf"
    metadata: dict[str, Any]
    source_url: str | None = None
    input_kind: str

    local = Path(value).expanduser()
    arxiv_id = parse_arxiv_id(value)
    if local.is_file():
        if local.suffix.lower() != ".pdf":
            raise SourceError("Local input must be a .pdf file.")
        if local.stat().st_size > max_bytes:
            raise SourceError(f"Local PDF exceeds the {max_bytes}-byte limit.")
        shutil.copy2(local, destination)
        input_kind = "local_pdf"
        metadata = {"arxiv": None, "doi": None, "title": None, "authors": [], "published": None, "updated": None, "license": "unknown"}
        source_name = "local-paper.pdf"
    elif arxiv_id:
        input_kind = "arxiv"
        source_url = f"https://arxiv.org/abs/{arxiv_id}"
        atom_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        atom = fetch_bytes(atom_url, max_bytes=DEFAULT_MAX_HTML_BYTES, session=session)
        metadata = _parse_arxiv_atom(atom.data, arxiv_id)
        fetched = fetch_bytes(f"https://arxiv.org/pdf/{arxiv_id}", max_bytes=max_bytes, session=session)
        if not _looks_like_pdf(fetched.data, fetched.content_type):
            raise SourceError("arXiv PDF endpoint did not return a PDF.")
        destination.write_bytes(fetched.data)
        source_name = f"{arxiv_id}.pdf"
    elif urlsplit(value).scheme:
        input_kind = "public_url"
        fetched = fetch_bytes(value, max_bytes=max_bytes, allow_http=allow_http, session=session)
        source_url = fetched.url
        if not _looks_like_pdf(fetched.data, fetched.content_type):
            if fetched.content_type not in {"text/html", "application/xhtml+xml", ""}:
                raise SourceError(f"URL returned unsupported content type: {fetched.content_type or 'unknown'}")
            if len(fetched.data) > DEFAULT_MAX_HTML_BYTES:
                raise SourceError("Landing page exceeds the safe HTML discovery limit.")
            pdf_url = _discover_pdf_url(fetched.data, fetched.url)
            fetched = fetch_bytes(pdf_url, max_bytes=max_bytes, allow_http=allow_http, session=session)
            if not _looks_like_pdf(fetched.data, fetched.content_type):
                raise SourceError("Discovered PDF link did not return a PDF.")
            source_url = fetched.url
            input_kind = "landing_page"
        destination.write_bytes(fetched.data)
        metadata = {"arxiv": None, "doi": None, "title": None, "authors": [], "published": None, "updated": None, "license": "unknown"}
        source_name = "remote-paper.pdf"
    else:
        raise SourceError("Input is neither an existing PDF, a supported arXiv identifier, nor a public URL.")

    if not destination.read_bytes()[:1024].lstrip().startswith(b"%PDF-"):
        raise SourceError("Input does not have a valid PDF header.")
    digest = sha256_file(destination)
    stable_hint = metadata.get("arxiv") or f"paper-{digest[:12]}"
    metadata.update(
        {
            "input_kind": input_kind,
            "source_name": Path(source_name).name,
            "source_url": public_url(source_url),
            "sha256": digest,
            "file_bytes": destination.stat().st_size,
            "stable_id": stable_slug(str(stable_hint), f"paper-{digest[:12]}"),
            "retrieved_at": utc_now(),
        }
    )
    write_json(output_dir / "resolution.json", metadata)
    return destination, metadata
