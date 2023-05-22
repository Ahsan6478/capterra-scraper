"""Export product data to CSV files."""

from __future__ import annotations

import csv
import logging
import os
from typing import Dict, List, Sequence

from capterra_scraper.models.product import Product

logger = logging.getLogger(__name__)


def export_products_csv(products: Sequence[Product], output_path: str) -> None:
    """Write a list of products to a CSV file.

    Parameters
    ----------
    products:
        Products to export.
    output_path:
        Full file path for the output CSV.
    """
    if not products:
        logger.warning("No products to export")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    rows = [p.to_dict() for p in products]
    fieldnames = list(rows[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Exported %d products to %s", len(products), output_path)


def export_products_csv_chunked(
    products: Sequence[Product],
    output_dir: str,
    chunk_size: int = 500,
) -> None:
    """Export products to multiple CSV files split by chunk size."""
    if not products:
        return

    os.makedirs(output_dir, exist_ok=True)

    for i in range(0, len(products), chunk_size):
        chunk = products[i : i + chunk_size]
        part = (i // chunk_size) + 1
        path = os.path.join(output_dir, f"capterra_products_part{part}.csv")
        export_products_csv(chunk, path)
        logger.info("Exported chunk %d (%d products)", part, len(chunk))
