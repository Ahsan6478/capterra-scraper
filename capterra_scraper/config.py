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


