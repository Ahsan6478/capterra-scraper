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


