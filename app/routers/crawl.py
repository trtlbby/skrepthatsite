from __future__ import annotations

from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crawlers.gutenberg import GutenbergCrawler
from app.crawlers.merlot import MERLOTCrawler
from app.crawlers.openstax import OpenStaxCrawler
from app.database import get_db
from app.models import CrawlLog, Resource, ResourceAuthor
from app.schemas import CrawlRequest, CrawlResponse
from app.services import deduplicator, normalizer

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_crawler(platform: str):
    if platform == "openstax":
        return OpenStaxCrawler()
    if platform == "gutenberg":
        return GutenbergCrawler()
    if platform == "merlot":
        return MERLOTCrawler()
    raise HTTPException(status_code=400, detail="Unsupported platform")


@router.post("", response_model=CrawlResponse)
def crawl_resources(payload: CrawlRequest, db: Session = Depends(get_db)):
    log = CrawlLog(platform=payload.platform, status="running")
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        crawler = _get_crawler(payload.platform)
        if not crawler.health_check():
            log.status = "failed"
            log.error_message = "platform unreachable"
            log.completed_at = datetime.utcnow()
            db.commit()
            return log

        raw_resources = crawler.crawl(limit=payload.limit)
        log.records_fetched = len(raw_resources)

        for raw in raw_resources:
            try:
                resource_data = normalizer.normalize(raw)
            except ValueError as exc:
                logger.warning("Normalization error: %s", exc)
                log.records_skipped += 1
                continue

            duplicate_id = deduplicator.find_duplicate(resource_data, db)
            if duplicate_id:
                log.records_skipped += 1
                continue

            authors = resource_data.pop("authors", [])
            resource = Resource(**resource_data)
            db.add(resource)
            db.flush()

            for author_name in authors:
                db.add(ResourceAuthor(resource_id=resource.resource_id, author_name=author_name))

            log.records_inserted += 1

        log.status = "completed"
        log.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(log)
        return log

    except Exception as exc:  # noqa: BLE001
        logger.exception("Crawl failed: %s", exc)
        log.status = "failed"
        log.error_message = str(exc)
        log.completed_at = datetime.utcnow()
        db.commit()
        return log
