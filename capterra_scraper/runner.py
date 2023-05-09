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


def run_product_extraction(
    client: CapterraHttpClient,
    product_urls: List[str],
    cookie: Optional[str] = None,
    num_threads: int = DEFAULT_THREADS,
    max_workers: int = MAX_THREAD_CAP,
    output_dir: str = "output",
) -> List[Product]:
    """Extract product details for a list of product URLs.

    Results are exported to both CSV and JSON in *output_dir*.
    """
    logger.info("Starting extraction for %d product URLs", len(product_urls))
    batches = _divide_list(product_urls, num_threads)
    all_products: List[Product] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_extract_batch, client, batch, cookie): idx
            for idx, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            batch_products = future.result()
            all_products.extend(batch_products)

    os.makedirs(output_dir, exist_ok=True)
    export_products_csv(all_products, os.path.join(output_dir, "capterra_products.csv"))
    export_products_json(all_products, os.path.join(output_dir, "capterra_products.json"))

    logger.info("Extraction complete: %d products", len(all_products))
    return all_products


def _extract_batch(
    client: CapterraHttpClient,
    urls: List[str],
    cookie: Optional[str],
) -> List[Product]:
    """Extract products for a batch of URLs."""
    products: List[Product] = []
    for url in urls:
        try:
            product = extract_product(client, url, cookie=cookie)
            if product is not None:
                products.append(product)
        except Exception:
            logger.exception("Failed to extract product: %s", url)
    return products
