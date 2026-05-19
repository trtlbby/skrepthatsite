from __future__ import annotations

from datetime import datetime
import json
import unicodedata

from subfolder.app.crawlers.base import RawResource


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return unicodedata.normalize("NFKC", value).strip()


def compute_quality_score(raw: RawResource) -> float:
    score = 0.0
    if raw.title:
        score += 0.20
    if raw.description and len(raw.description) > 50:
        score += 0.20
    if raw.authors:
        score += 0.15
    if raw.publication_year:
        score += 0.15
    if raw.isbn or raw.doi:
        score += 0.10
    if len(raw.subject_tags) > 0:
        score += 0.10
    if raw.license_type:
        score += 0.10
    authority = {"openstax": 1.0, "merlot": 0.8, "gutenberg": 0.6}.get(
        raw.source_platform, 0.5
    )
    score = score * authority
    return round(min(score, 1.0), 4)


def normalize(raw: RawResource) -> dict:
    title = _clean_text(raw.title)
    if not title:
        raise ValueError("title is required")

    description = _clean_text(raw.description)

    authors = []
    seen = set()
    for author in raw.authors:
        cleaned = _clean_text(author)
        if cleaned and cleaned.lower() not in seen:
            authors.append(cleaned)
            seen.add(cleaned.lower())

    publication_year = raw.publication_year
    current_year = datetime.utcnow().year
    if not publication_year or not (1900 <= publication_year <= current_year):
        publication_year = None

    url = (raw.url or "").strip()
    if not url.startswith("http"):
        raise ValueError(f"invalid url: {url}")

    isbn = None
    if raw.isbn:
        cleaned_isbn = raw.isbn.replace("-", "").replace(" ", "").strip()
        if len(cleaned_isbn) in (10, 13):
            isbn = cleaned_isbn

    return {
        "title": title,
        "description": description,
        "publication_year": publication_year,
        "source_type": raw.source_type,
        "source_platform": raw.source_platform,
        "url": url,
        "isbn": isbn,
        "doi": raw.doi,
        "license_type": raw.license_type,
        "lifecycle_status": "active",
        "date_ingested": datetime.utcnow(),
        "quality_score": compute_quality_score(raw),
        "embedding": None,
        "duplicate_source_ids": json.dumps([]),
        "authors": authors,
    }
