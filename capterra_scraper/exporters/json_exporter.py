"""Export product data to JSON files."""

from __future__ import annotations

import json
import logging
import os
from typing import Sequence

from capterra_scraper.models.product import Product

logger = logging.getLogger(__name__)


def export_products_json(products: Sequence[Product], output_path: str) -> None:
    """Write a list of products to a JSON file.

    Parameters
    ----------
    products:
        Products to export.
    output_path:
        Full file path for the output JSON.
    """
    if not products:
        logger.warning("No products to export")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = [p.to_dict() for p in products]
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    logger.info("Exported %d products to %s", len(products), output_path)


def merge_json_files(directory: str, output_path: str) -> int:
    """Merge per-thread JSON files into one deduplicated file.

    Deduplicates on ``(product_id, category_name)`` pairs.

    Returns the number of unique records written.
    """
    merged: list[dict] = []

    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(directory, filename)
        with open(filepath, "r", encoding="utf-8") as fh:
            try:
                records = json.load(fh)
                if isinstance(records, list):
                    merged.extend(records)
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSON file: %s", filepath)

    seen: set = set()
    unique: list[dict] = []
    for record in merged:
        key = (record.get("product_id"), record.get("category_name"))
        if key not in seen:
            seen.add(key)
            unique.append(record)

    # Fix double-slash URLs
    for record in unique:
        url = record.get("capterra_url", "")
        if "//p" in url:
            record["capterra_url"] = url.replace("//p", "/p")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(unique, fh, indent=2, ensure_ascii=False)

    logger.info("Merged %d unique records from %s", len(unique), directory)
    return len(unique)
