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


def fetch_product_urls_for_category(
    client: CapterraHttpClient,
    category_path: str,
    cookie: Optional[str] = None,
) -> Optional[CategoryInfo]:
    """Paginate through a category listing and collect all product URLs.

    Returns a :class:`CategoryInfo` with the product URL list, or *None*
    if the category could not be scraped.
    """
    page = 1
    product_urls: List[str] = []
    category_name = ""
    capterra_count = 0
    category_url = ""

    while True:
        endpoint = f"{category_path}?page={page}"
        resp = _fetch_with_retries(client, endpoint, cookie)

        if resp is None or resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        if page == 1:
            category_url = endpoint
            count_div = soup.find("div", {"data-testid": "amount-of-products"})
            if count_div:
                try:
                    capterra_count = int(
                        count_div.text.split("(")[1].split(")")[0].strip()
                    )
                except (IndexError, ValueError):
                    capterra_count = 0

            h1 = soup.find("h1", {"class": "text-xl font-bold md:text-3xl"})
            category_name = h1.text if h1 else ""

        cards = soup.find_all("div", {"class": "p-md"})
        page_urls = [div.find("a")["href"] for div in cards if div.find("a")]

        if not page_urls:
            break

        product_urls.extend(page_urls)
        page += 1

    if not product_urls:
        return None

    unique_urls = list(set(product_urls))
    logger.info(
        "Category '%s': found %d products (Capterra reports %d)",
        category_name,
        len(unique_urls),
        capterra_count,
    )

    return CategoryInfo(
        name=category_name,
        url=category_url,
        capterra_count=capterra_count,
        product_urls=unique_urls,
    )


def _fetch_with_retries(client, endpoint, cookie, max_retries=MAX_RETRIES):
    """Try fetching an endpoint, refreshing cookies on 403 errors."""
    retry_count = 0
    while True:
        try:
            resp = client.get(endpoint, cookie=cookie)
            retry_count += 1
            logger.debug("GET %s -> %d", endpoint, resp.status_code)

            if resp.status_code in (200, 404):
                return resp
            if resp.status_code == 403 and retry_count >= max_retries:
                cookie = refresh_cookie()
                retry_count = 0
        except Exception:
            logger.exception("Request error for %s", endpoint)
            retry_count += 1
            if retry_count > max_retries:
                return None
