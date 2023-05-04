"""Cookie generation via external API."""

from __future__ import annotations

import json
import logging
from typing import Optional

import requests

from capterra_scraper.config import CookieServiceConfig

logger = logging.getLogger(__name__)


def refresh_cookie(config: Optional[CookieServiceConfig] = None) -> Optional[str]:
    """Request a fresh cookie from the cookie-generation API.

    Returns the cookie string on success, or *None* if the API does not
    return a valid cookie.
    """
    if config is None:
        config = CookieServiceConfig.from_env()

    if not config.auth_token:
        logger.warning("No cookie auth token configured; skipping refresh")
        return None

    payload = json.dumps({
        "auth": config.auth_token,
        "site": config.site,
        "proxyregion": config.proxy_region,
        "region": config.region,
        "proxy": config.auth_token,
    })

    try:
        resp = requests.post(config.url, headers={"Content-Type": "application/json"}, data=payload)
        resp.raise_for_status()
        data = resp.json()
        cookie = data.get("cookie")
        if cookie:
            logger.info("Cookie refreshed successfully")
        else:
            logger.warning("Cookie API returned no cookie: %s", data)
        return cookie
    except requests.RequestException:
        logger.exception("Failed to refresh cookie")
        return None
