"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class ProxyConfig:
    """Proxy connection settings."""

    host: str = ""
    port: int = 22225
    username: str = ""
    password: str = ""

    @classmethod
    def from_env(cls) -> "ProxyConfig":
        """Build proxy config from ``CAPTERRA_PROXY_*`` environment variables."""
        return cls(
            host=os.environ.get("CAPTERRA_PROXY_HOST", ""),
            port=int(os.environ.get("CAPTERRA_PROXY_PORT", "22225")),
            username=os.environ.get("CAPTERRA_PROXY_USER", ""),
            password=os.environ.get("CAPTERRA_PROXY_PASS", ""),
        )


@dataclass(frozen=True)
class CookieServiceConfig:
    """Settings for the cookie generation API."""

    url: str = "https://api.parallaxsystems.io/gen"
    auth_token: str = ""
    site: str = "capterra"
    proxy_region: str = "eu"
    region: str = "com"

    @classmethod
    def from_env(cls) -> "CookieServiceConfig":
        """Build cookie-service config from environment variables."""
        return cls(
            url=os.environ.get("CAPTERRA_COOKIE_API_URL", "https://api.parallaxsystems.io/gen"),
            auth_token=os.environ.get("CAPTERRA_COOKIE_AUTH", ""),
            proxy_region=os.environ.get("CAPTERRA_COOKIE_PROXY_REGION", "eu"),
            region=os.environ.get("CAPTERRA_COOKIE_REGION", "com"),
        )


