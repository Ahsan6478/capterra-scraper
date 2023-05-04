"""Spider for extracting individual product details from Capterra pages."""

from __future__ import annotations

import json
import logging
from typing import Optional

from bs4 import BeautifulSoup

from capterra_scraper.config import MAX_RETRIES
from capterra_scraper.models.product import Product
from capterra_scraper.services.cookie_manager import refresh_cookie
from capterra_scraper.services.http_client import CapterraHttpClient

logger = logging.getLogger(__name__)


def extract_product(
    client: CapterraHttpClient,
    url: str,
    cookie: Optional[str] = None,
) -> Optional[Product]:
    """Fetch a product page and parse the SSR bridge data.

    Returns a :class:`Product` on success or *None* if the page could
    not be fetched or parsed.
    """
    retry_count = 0

    while True:
        try:
            resp = client.get(url, cookie=cookie)
            retry_count += 1
            logger.debug("GET %s -> %d", url, resp.status_code)

            if resp.status_code == 404:
                logger.warning("Product page not found: %s", url)
                return None
            if resp.status_code == 200:
                break
            if resp.status_code == 403 and retry_count >= MAX_RETRIES:
                cookie = refresh_cookie()
                retry_count = 0
        except Exception:
            logger.exception("Error fetching product %s", url)
            retry_count += 1
            if retry_count > MAX_RETRIES:
                return None

    return _parse_ssr_bridge_data(resp.text)


def _parse_ssr_bridge_data(html: str) -> Optional[Product]:
    """Extract and parse the ``SSR_BRIDGE_DATA`` JSON embedded in the page."""
    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script"):
        script_text = str(script.string) if script.string else ""
        if (
            "SSR_BRIDGE_DATA" in script_text
            and "rank" in script_text
            and "alternativeProducts" in script_text
        ):
            cleaned = script_text.replace("window['SSR_BRIDGE_DATA'] =", "").strip()
            try:
                raw_data = json.loads(cleaned)
                return Product.from_ssr_data(raw_data)
            except (json.JSONDecodeError, KeyError, TypeError):
                logger.exception("Failed to parse SSR_BRIDGE_DATA")
                return None

    logger.warning("No SSR_BRIDGE_DATA script tag found")
    return None
