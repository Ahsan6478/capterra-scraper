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

