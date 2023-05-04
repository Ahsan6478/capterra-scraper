"""HTTP client with proxy tunnel support for Capterra requests."""

from __future__ import annotations

import base64
import http.client
import logging
from copy import deepcopy
from typing import Any, Dict, Optional

from capterra_scraper.config import DEFAULT_HEADERS, ProxyConfig

logger = logging.getLogger(__name__)


class HttpResponse:
    """Thin wrapper around an HTTP response."""

    __slots__ = ("status_code", "text", "content")

    def __init__(self, status_code: int, text: str, content: bytes) -> None:
        self.status_code = status_code
        self.text = text
        self.content = content

    def __repr__(self) -> str:
        return f"<HttpResponse status={self.status_code} len={len(self.text)}>"


