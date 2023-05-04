"""Spider for discovering Capterra software categories and their product URLs."""

from __future__ import annotations

import logging
from typing import List, Optional

from bs4 import BeautifulSoup

from capterra_scraper.config import MAX_RETRIES
from capterra_scraper.models.product import CategoryInfo
from capterra_scraper.services.cookie_manager import refresh_cookie
from capterra_scraper.services.http_client import CapterraHttpClient

logger = logging.getLogger(__name__)


def fetch_category_urls(client: CapterraHttpClient, cookie: Optional[str] = None) -> List[str]:
    """Fetch the master list of category URLs from the /categories/ page.

    Returns a list of relative category paths such as
    ``/accounting-software/``.
    """
    endpoint = "/categories/"
    retry_count = 0

    while True:
        try:
            resp = client.get(endpoint, cookie=cookie)
            retry_count += 1
            logger.info("GET %s -> %d", endpoint, resp.status_code)

            if resp.status_code == 200:
                break
            if resp.status_code == 403 and retry_count >= MAX_RETRIES:
                cookie = refresh_cookie()
                retry_count = 0
        except Exception:
            logger.exception("Error fetching categories, retrying")
            continue

    soup = BeautifulSoup(resp.text, "html.parser")
    container = soup.find("div", {"data-testid": "alphabetical-list"})
    if container is None:
        logger.error("Could not find alphabetical-list container")
        return []

    urls: List[str] = []
    for li in container.find_all("li"):
        anchor = li.find("a")
        if anchor and anchor.get("href"):
            urls.append(anchor["href"])

    logger.info("Discovered %d category URLs", len(urls))
    return urls


