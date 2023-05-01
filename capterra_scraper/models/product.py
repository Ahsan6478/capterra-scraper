"""Product and category data models."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CategoryInfo:
    """Represents a Capterra software category."""

    name: str
    url: str
    capterra_count: int = 0
    product_urls: List[str] = field(default_factory=list)

    @property
    def scraped_count(self) -> int:
        return len(self.product_urls)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Product:
    """Represents a single software product scraped from Capterra."""

    category_url: str = ""
    category_id: Optional[int] = None
    category_name: str = ""
    product_id: Optional[int] = None
    name: str = ""
    website: str = ""
    rating: Optional[float] = None
    review_count: int = 0
    capterra_url: str = ""
    vendor_name: str = ""
    description: str = ""
    long_description: str = ""
    year_founded: Optional[int] = None
    value_for_money_rating: Optional[float] = None
    customer_service_rating: Optional[float] = None
    ease_of_use_rating: Optional[float] = None
    recommendation_rating: Optional[float] = None
    functionality_rating: Optional[float] = None
    pricing_overview: str = ""
    pricing: str = ""
    location: str = ""
    has_free_trial: bool = False
    training: List[str] = field(default_factory=list)
    support: List[str] = field(default_factory=list)
    best_for: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_ssr_data(cls, raw: Dict[str, Any]) -> "Product":
        """Parse a product from Capterra's ``SSR_BRIDGE_DATA`` JSON payload."""
        category = raw.get("category", {})
        vendor = raw.get("vendor", {})

        category_html = category.get("htmlName", "")
        if not category_html.startswith("/"):
            category_html = "/" + category_html
        category_url = "https://www.capterra.com" + category_html

        product_path = raw.get("productUrl", "")
        if not product_path.startswith("/"):
            product_path = "/" + product_path
        capterra_url = "https://www.capterra.com" + product_path

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return cls(
            category_url=category_url,
            category_id=category.get("id"),
            category_name=category.get("longName", ""),
            product_id=raw.get("productId"),
            name=raw.get("name", ""),
            website=vendor.get("url", ""),
            rating=raw.get("overallRating"),
            review_count=raw.get("reviewsTotal", 0),
            capterra_url=capterra_url,
            vendor_name=vendor.get("name", ""),
            description=raw.get("shortDescription", ""),
            long_description=raw.get("longDescription", ""),
            year_founded=vendor.get("yearFounded"),
            value_for_money_rating=raw.get("valueForMoneyRating"),
            customer_service_rating=raw.get("customerServiceRating"),
            ease_of_use_rating=raw.get("easeOfUseRating"),
            recommendation_rating=raw.get("recommendationRating"),
            functionality_rating=raw.get("functionalityRating"),
            pricing_overview=raw.get("pricingDetails", ""),
            pricing=raw.get("pricing", ""),
            location=vendor.get("location", ""),
            has_free_trial=raw.get("hasFreeTrial", False),
            training=[item["name"] for item in raw.get("training", [])],
            support=[item["name"] for item in raw.get("support", [])],
            best_for=raw.get("bestFor", ""),
            created_at=now,
            updated_at=now,
        )
