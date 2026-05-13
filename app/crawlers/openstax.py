from __future__ import annotations

from datetime import datetime
import logging

import httpx

from app.crawlers.base import BaseCrawler, RawResource

logger = logging.getLogger(__name__)


class OpenStaxCrawler(BaseCrawler):
    API_URL = "https://openstax.org/api/v2/books?format=json"
    BASE_URL = "https://openstax.org/details/books"

    def crawl(self, limit: int = 50) -> list[RawResource]:
        try:
            response = httpx.get(self.API_URL, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.exception("OpenStax crawl failed: %s", exc)
            return []

        books = data if isinstance(data, list) else data.get("results", [])
        results: list[RawResource] = []

        for book in books[:limit]:
            authors = book.get("authors") or []
            author_names: list[str] = []
            if isinstance(authors, list):
                for author in authors:
                    if isinstance(author, dict):
                        name = author.get("name")
                    else:
                        name = str(author)
                    if name:
                        author_names.append(name)
            elif isinstance(authors, str):
                author_names = [authors]

            slug = book.get("slug")
            if not slug:
                continue

            resource = RawResource(
                source_platform="openstax",
                source_id=str(slug),
                title=self._clean_text(book.get("title")) or "",
                authors=author_names,
                description=self._clean_text(book.get("description")),
                publication_year=self._safe_year(book.get("publish_date")),
                url=f"{self.BASE_URL}/{slug}",
                isbn=book.get("isbn_13"),
                doi=None,
                license_type=None,
                source_type="textbook",
                subject_tags=book.get("subjects") or [],
                raw_payload=book,
                fetched_at=datetime.utcnow(),
            )
            results.append(resource)

        return results

    def health_check(self) -> bool:
        try:
            response = httpx.get("https://openstax.org", timeout=10.0)
            return response.status_code < 400
        except httpx.HTTPError:
            return False
