"""Tests for configuration module."""

import os

from capterra_scraper.config import ProxyConfig, CookieServiceConfig, BASE_URL


class TestProxyConfig:
    def test_defaults(self):
        config = ProxyConfig()
        assert config.host == ""
        assert config.port == 22225

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("CAPTERRA_PROXY_HOST", "test.proxy")
        monkeypatch.setenv("CAPTERRA_PROXY_PORT", "9999")
        monkeypatch.setenv("CAPTERRA_PROXY_USER", "admin")
        monkeypatch.setenv("CAPTERRA_PROXY_PASS", "secret")

        config = ProxyConfig.from_env()
        assert config.host == "test.proxy"
        assert config.port == 9999
        assert config.username == "admin"

