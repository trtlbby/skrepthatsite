from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawResource:
    source_platform: str
    source_id: str
    title: str
    authors: list[str]
    description: str | None
    publication_year: int | None
    url: str
    isbn: str | None
    doi: str | None
    license_type: str | None
    source_type: str | None
    subject_tags: list[str]
    raw_payload: dict
    fetched_at: datetime


class BaseCrawler(ABC):
    @abstractmethod
    def crawl(self, limit: int = 50) -> list[RawResource]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

    def _safe_year(self, value) -> int | None:
        """Extract a valid 4-digit year from any value. Return None if unparseable."""
        try:
            year = int(str(value)[:4])
            if 1900 <= year <= datetime.now().year:
                return year
        except (ValueError, TypeError):
            pass
        return None

    def _clean_text(self, value: str | None) -> str | None:
        """Normalize unicode and strip whitespace."""
        if not value:
            return None
        import unicodedata

        return unicodedata.normalize("NFKC", value).strip()
