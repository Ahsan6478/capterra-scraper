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


