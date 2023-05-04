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


class CapterraHttpClient:
    """Makes GET requests to Capterra through an HTTPS proxy tunnel.

    Parameters
    ----------
    proxy_config:
        Proxy host / port / credentials.  When *None*, a direct connection
        to ``www.capterra.com`` is used (useful for testing).
    """

    HOST = "www.capterra.com"

    def __init__(self, proxy_config: Optional[ProxyConfig] = None) -> None:
        self._proxy = proxy_config
        self._headers: Dict[str, str] = deepcopy(DEFAULT_HEADERS)

    def _build_auth_hash(self) -> str:
        if self._proxy is None:
            return ""
        creds = f"{self._proxy.username}:{self._proxy.password}"
        return base64.b64encode(creds.encode()).decode()

    def get(self, endpoint: str, cookie: Optional[str] = None) -> HttpResponse:
        """Perform a GET request.

        Parameters
        ----------
        endpoint:
            Path portion of the URL (e.g. ``/software/category-name``).
            A full URL starting with ``https://www.capterra.com`` is also
            accepted and will be stripped automatically.
        cookie:
            Optional cookie string to attach to the request.
        """
        endpoint = str(endpoint).replace("https://www.capterra.com", "")

        headers = deepcopy(self._headers)
        if cookie:
            headers["cookie"] = cookie

        if self._proxy and self._proxy.host:
            conn = http.client.HTTPSConnection(self._proxy.host, port=self._proxy.port)
            auth_hash = self._build_auth_hash()
            conn.set_tunnel(self.HOST, headers={"Proxy-Authorization": f"Basic {auth_hash}"})
        else:
            conn = http.client.HTTPSConnection(self.HOST)

        conn.request("GET", endpoint, body="", headers=headers)
        resp = conn.getresponse()
        raw = resp.read()

        return HttpResponse(
            status_code=resp.status,
            text=raw.decode("utf-8", errors="replace"),
            content=raw,
        )
