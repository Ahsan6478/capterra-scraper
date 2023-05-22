"""Web spiders for crawling Capterra."""

from capterra_scraper.spiders.category_spider import fetch_category_urls
from capterra_scraper.spiders.product_spider import extract_product

__all__ = ["fetch_category_urls", "extract_product"]
