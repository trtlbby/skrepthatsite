from __future__ import annotations

from datetime import datetime
import logging
import re
import time

import httpx

from app.crawlers.base import BaseCrawler, RawResource

logger = logging.getLogger(__name__)


class OpenStaxCrawler(BaseCrawler):
    API_URL = "https://openstax.org/apps/cms/api/books"
    BASE_URL = "https://openstax.org/details/books"

    def crawl(self, limit: int = 50) -> list[RawResource]:
        try:
            response = httpx.get(self.API_URL, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.exception("OpenStax crawl failed: %s", exc)
            return []

        books = data.get("books", []) if isinstance(data, dict) else data
        if not isinstance(books, list):
            books = []

        results: list[RawResource] = []

        for book in books[:limit]:
            slug_raw = book.get("slug")
            if not slug_raw:
                continue
                
            # Slugs might come as "books/additive-manufacturing-essentials"
            slug = slug_raw.replace("books/", "")
            
            try:
                detail_resp = httpx.get(f"{self.API_URL}/{slug}", timeout=30.0, follow_redirects=True)
                detail_resp.raise_for_status()
                detail = detail_resp.json()
            except (httpx.HTTPError, ValueError) as exc:
                logger.warning("Failed to fetch detail for %s: %s", slug, exc)
                continue

            authors_data = detail.get("authors") or []
            author_names: list[str] = []
            if isinstance(authors_data, list):
                for author in authors_data:
                    if isinstance(author, dict) and "value" in author:
                        name = author["value"].get("name")
                        if name:
                            author_names.append(name)
            
            # Clean HTML tags from description
            desc_raw = detail.get("description") or ""
            desc_clean = re.sub(r"<[^>]+>", "", desc_raw).strip()

            resource = RawResource(
                source_platform="openstax",
                source_id=str(slug),
                title=self._clean_text(detail.get("title")) or self._clean_text(book.get("title")) or "",
                authors=author_names,
                description=self._clean_text(desc_clean),
                publication_year=self._safe_year(detail.get("publish_date")),
                url=f"{self.BASE_URL}/{slug}",
                isbn=detail.get("print_isbn_13") or detail.get("digital_isbn_13"),
                doi=None,
                license_type=None,
                source_type="textbook",
                subject_tags=detail.get("subjects") or book.get("subjects") or [],
                raw_payload=detail,
                fetched_at=datetime.utcnow(),
            )
            results.append(resource)
            time.sleep(0.5)

        return results

    def health_check(self) -> bool:
        try:
            response = httpx.get("https://openstax.org", timeout=10.0, follow_redirects=True)
            return response.status_code < 400
        except httpx.HTTPError:
            return False
