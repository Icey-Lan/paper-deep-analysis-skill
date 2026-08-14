from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlsplit


ARXIV_ID_RE = re.compile(
    r"^(?P<id>(?:[a-z-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?)$",
    re.IGNORECASE,
)
ARXIV_URL_RE = re.compile(
    r"^https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/(?P<id>[^?#]+?)(?:\.pdf)?/?$",
    re.IGNORECASE,
)
DEFAULT_MAX_BYTES = 50 * 1024 * 1024


class InputGuardError(RuntimeError):
    pass


def parse_arxiv_id(value: str) -> str | None:
    value = value.strip()
    match = ARXIV_ID_RE.match(value)
    if match:
        return match.group("id")
    match = ARXIV_URL_RE.match(value)
    if match:
        return match.group("id")
    return None


def guard_url(url: str, *, allow_http: bool = False) -> None:
    parts = urlsplit(url)
    allowed_schemes = {"https"} | ({"http"} if allow_http else set())
    if parts.scheme.lower() not in allowed_schemes:
        raise InputGuardError("Only public HTTPS URLs are allowed by default.")
    if parts.username or parts.password:
        raise InputGuardError("URLs containing credentials are not allowed.")
    if not parts.hostname:
        raise InputGuardError("URL has no hostname.")
    try:
        infos = socket.getaddrinfo(parts.hostname, parts.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise InputGuardError(f"Could not resolve URL hostname: {parts.hostname}") from exc
    addresses = {info[4][0].split("%", 1)[0] for info in infos}
    if not addresses:
        raise InputGuardError("URL hostname resolved to no addresses.")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise InputGuardError(f"Blocked non-public network address for {parts.hostname}.")
