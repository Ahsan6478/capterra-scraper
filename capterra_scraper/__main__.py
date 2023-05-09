"""CLI entry point for the Capterra scraper.

Usage::

    python -m capterra_scraper [--threads N] [--max-workers N] [--output DIR]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from capterra_scraper.config import DEFAULT_THREADS, MAX_THREAD_CAP, ProxyConfig
from capterra_scraper.runner import run_category_discovery, run_product_extraction
from capterra_scraper.services.http_client import CapterraHttpClient


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("capterra_scraper.log"),
        ],
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capterra product scraper")
    parser.add_argument(
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
        help=f"Number of thread groups (default: {DEFAULT_THREADS})",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_THREAD_CAP,
        help=f"Max concurrent threads (default: {MAX_THREAD_CAP})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--categories-file",
        type=str,
        default=None,
        help="Path to existing categories JSON to skip discovery",
    )
    return parser.parse_args()


def main() -> None:
    _setup_logging()
    args = _parse_args()

    proxy_config = ProxyConfig.from_env()
    client = CapterraHttpClient(proxy_config=proxy_config if proxy_config.host else None)

    cookie = os.environ.get("CAPTERRA_COOKIE", "")

    # Phase 1: Category discovery
    if args.categories_file and os.path.exists(args.categories_file):
        logging.info("Loading categories from %s", args.categories_file)
        with open(args.categories_file, "r") as fh:
            categories = json.load(fh)
    else:
        categories = run_category_discovery(
            client,
            cookie=cookie or None,
            num_threads=args.threads,
            max_workers=args.max_workers,
        )
        os.makedirs(args.output, exist_ok=True)
        cat_path = os.path.join(args.output, "categories.json")
        with open(cat_path, "w") as fh:
            json.dump(categories, fh, indent=2)
        logging.info("Saved %d categories to %s", len(categories), cat_path)

    # Phase 2: Product extraction
    all_product_urls: list[str] = []
    for cat in categories:
        all_product_urls.extend(cat.get("product_urls", []))

    unique_urls = list(set(all_product_urls))
    logging.info("Total unique product URLs: %d", len(unique_urls))

    if unique_urls:
        run_product_extraction(
            client,
            unique_urls,
            cookie=cookie or None,
            num_threads=args.threads,
            max_workers=args.max_workers,
            output_dir=args.output,
        )


if __name__ == "__main__":
    main()
