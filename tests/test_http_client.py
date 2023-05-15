"""Tests for the HTTP client."""

from capterra_scraper.config import ProxyConfig
from capterra_scraper.services.http_client import CapterraHttpClient, HttpResponse


class TestHttpResponse:
    def test_repr(self):
        resp = HttpResponse(200, "hello", b"hello")
        assert "200" in repr(resp)
        assert "5" in repr(resp)

    def test_attributes(self):
        resp = HttpResponse(404, "not found", b"not found")
        assert resp.status_code == 404
        assert resp.text == "not found"


class TestCapterraHttpClient:
    def test_init_without_proxy(self):
        client = CapterraHttpClient()
        assert client._proxy is None

    def test_init_with_proxy(self):
        proxy = ProxyConfig(host="proxy.test", port=8080, username="u", password="p")
        client = CapterraHttpClient(proxy_config=proxy)
        assert client._proxy.host == "proxy.test"

    def test_auth_hash_without_proxy(self):
        client = CapterraHttpClient()
        assert client._build_auth_hash() == ""

    def test_auth_hash_with_proxy(self):
        proxy = ProxyConfig(host="h", port=1, username="user", password="pass")
        client = CapterraHttpClient(proxy_config=proxy)
        auth = client._build_auth_hash()
        assert len(auth) > 0
