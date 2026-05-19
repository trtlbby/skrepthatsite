from __future__ import annotations

from datetime import datetime
import logging
import time

from bs4 import BeautifulSoup
import requests

from subfolder.app.crawlers.base import BaseCrawler, RawResource

logger = logging.getLogger(__name__)


class GutenbergCrawler(BaseCrawler):
    BASE_URL = "https://www.gutenberg.org/ebooks/bookshelf/671"

    def crawl(self, limit: int = 50) -> list[RawResource]:
        results: list[RawResource] = []
        start_index = 0

        while len(results) < limit:
            url = f"{self.BASE_URL}?start_index={start_index}"
            try:
                response = requests.get(url, timeout=20.0)
                response.raise_for_status()
            except requests.RequestException as exc:
                logger.exception("Gutenberg crawl failed: %s", exc)
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            entries = soup.select("li.booklink")
            if not entries:
                break

            for entry in entries:
                if len(results) >= limit:
                    break

                title = entry.select_one("span.title")
                author = entry.select_one("span.subtitle")
                link = entry.select_one("a.link")
                extra = entry.select_one("span.extra")

                href = link["href"] if link and link.has_attr("href") else None
                if not href:
                    continue

                resource = RawResource(
                    source_platform="gutenberg",
                    source_id=href,
                    title=self._clean_text(title.get_text()) if title else "",
                    authors=[self._clean_text(author.get_text())] if author else [],
                    description=None,
                    publication_year=None,
                    url=f"https://www.gutenberg.org{href}",
                    isbn=None,
                    doi=None,
                    license_type="public domain",
                    source_type="book",
                    subject_tags=["computer science"],
                    raw_payload={"downloads": extra.get_text().strip() if extra else None},
                    fetched_at=datetime.utcnow(),
                )
                results.append(resource)

            start_index += 25
            time.sleep(1.0)

        return results

    def health_check(self) -> bool:
        try:
            response = requests.get("https://www.gutenberg.org", timeout=10.0)
            return response.status_code < 400
        except requests.RequestException:
            return False
