from __future__ import annotations

from rapidfuzz import fuzz

from subfolder.app.models import Resource


def find_duplicate(resource_dict: dict, db) -> str | None:
    """
    Returns existing resource_id if a duplicate is found, else None.
    Checks in this order: DOI -> ISBN -> URL
    """

    doi = resource_dict.get("doi")
    if doi:
        existing = db.query(Resource).filter(Resource.doi == doi).first()
        if existing:
            return existing.resource_id

    isbn = resource_dict.get("isbn")
    if isbn:
        existing = db.query(Resource).filter(Resource.isbn == isbn).first()
        if existing:
            return existing.resource_id

    url = resource_dict.get("url")
    if url:
        existing = db.query(Resource).filter(Resource.url == url).first()
        if existing:
            return existing.resource_id

    return None


def soft_dedup_score(
    title_a: str, authors_a: list[str], title_b: str, authors_b: list[str]
) -> float:
    """
    Returns a float 0.0-1.0 similarity score.
    Uses rapidfuzz.fuzz.token_sort_ratio on title (weight 0.7)
    and author string (weight 0.3).
    """

    title_score = fuzz.token_sort_ratio(title_a or "", title_b or "") / 100.0
    authors_score = fuzz.token_sort_ratio(
        " ".join(authors_a or []), " ".join(authors_b or [])
    ) / 100.0
    return round((title_score * 0.7) + (authors_score * 0.3), 4)
