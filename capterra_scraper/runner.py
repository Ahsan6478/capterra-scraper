"""Main orchestrator for the Capterra scraping pipeline."""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

from capterra_scraper.config import (
    DEFAULT_THREADS,
    MAX_THREAD_CAP,
    ProxyConfig,
)
from capterra_scraper.exporters.csv_exporter import export_products_csv
from capterra_scraper.exporters.json_exporter import export_products_json, merge_json_files
from capterra_scraper.models.product import Product
from capterra_scraper.services.http_client import CapterraHttpClient
from capterra_scraper.spiders.category_spider import (
    fetch_category_urls,
    fetch_product_urls_for_category,
)
from capterra_scraper.spiders.product_spider import extract_product

logger = logging.getLogger(__name__)


def _divide_list(items: list, n: int) -> List[list]:
    """Split *items* into *n* roughly equal sublists."""
    if n <= 0:
        return [items]
    base_size = len(items) // n
    remainder = len(items) % n
    result: List[list] = []
    start = 0
    for i in range(n):
        chunk_size = base_size + (1 if i < remainder else 0)
        result.append(items[start : start + chunk_size])
        start += chunk_size
    return result


def run_category_discovery(
    client: CapterraHttpClient,
    cookie: Optional[str] = None,
    num_threads: int = DEFAULT_THREADS,
    max_workers: int = MAX_THREAD_CAP,
) -> List[dict]:
    """Discover all categories and collect their product URLs.

    Returns a list of category dicts ready for JSON serialization.
    """
    category_paths = fetch_category_urls(client, cookie=cookie)
    if not category_paths:
        logger.error("No categories found, aborting discovery")
        return []

    logger.info("Starting product URL discovery for %d categories", len(category_paths))
    batches = _divide_list(category_paths, num_threads)
    results: List[dict] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_scrape_category_batch, client, batch, cookie): idx
            for idx, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            batch_results = future.result()
            results.extend(batch_results)

    logger.info("Discovered %d categories with product URLs", len(results))
    return results


def _scrape_category_batch(
    client: CapterraHttpClient,
    category_paths: List[str],
    cookie: Optional[str],
) -> List[dict]:
    """Scrape product URLs for a batch of category paths."""
    batch_results: List[dict] = []
    for path in category_paths:
        try:
            info = fetch_product_urls_for_category(client, path, cookie=cookie)
            if info is not None:
                batch_results.append(info.to_dict())
        except Exception:
            logger.exception("Failed to scrape category: %s", path)
    return batch_results


