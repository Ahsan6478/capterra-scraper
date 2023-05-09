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


