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


