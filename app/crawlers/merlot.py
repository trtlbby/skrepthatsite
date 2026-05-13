from __future__ import annotations

from datetime import datetime
import logging
import os
import time

from dotenv import load_dotenv
import httpx

from app.crawlers.base import BaseCrawler, RawResource

logger = logging.getLogger(__name__)

load_dotenv()


class MERLOTCrawler(BaseCrawler):
    API_URL = "https://www.merlot.org/merlot/materials.json"

    def crawl(self, limit: int = 50) -> list[RawResource]:
        api_key = os.getenv("MERLOT_API_KEY", "")
        if not api_key or api_key == "your_merlot_api_key_here":
            logger.warning("MERLOT_API_KEY is not set; skipping MERLOT crawl.")
            return []

        results: list[RawResource] = []
        page = 1

        while len(results) < limit:
            params = {
                "keywords": "computer science",
                "page": page,
                "pageSize": 25,
                "apikey": api_key,
            }
            try:
                response = httpx.get(self.API_URL, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                logger.exception("MERLOT crawl failed: %s", exc)
                return []

            materials = data.get("materials") or data.get("results") or []
            if not materials:
                break

            for material in materials:
                if len(results) >= limit:
                    break

                author_data = material.get("authorName") or []
                if isinstance(author_data, list):
                    authors = [str(name) for name in author_data if str(name).strip()]
                elif isinstance(author_data, str):
                    authors = [author_data]
                else:
                    authors = []

                url = material.get("url") or material.get("detailURL") or ""
                resource = RawResource(
                    source_platform="merlot",
                    source_id=str(material.get("id") or material.get("materialId") or url),
                    title=self._clean_text(material.get("title")) or "",
                    authors=authors,
                    description=self._clean_text(material.get("description")),
                    publication_year=self._safe_year(material.get("creationDate")),
                    url=url,
                    isbn=None,
                    doi=None,
                    license_type=material.get("license") or material.get("licenseName"),
                    source_type=material.get("materialType"),
                    subject_tags=material.get("subjects") or [],
                    raw_payload=material,
                    fetched_at=datetime.utcnow(),
                )
                results.append(resource)

            page += 1
            time.sleep(2.0)

        return results

    def health_check(self) -> bool:
        try:
            response = httpx.get("https://www.merlot.org", timeout=10.0)
            return response.status_code < 400
        except httpx.HTTPError:
            return False
