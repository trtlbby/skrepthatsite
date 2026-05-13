from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Resource, Topic
from app.schemas import MatchRequest, MatchResponse
from app.services import matcher

router = APIRouter()


@router.post("", response_model=MatchResponse)
def match_resources(payload: MatchRequest, db: Session = Depends(get_db)):
    topics = db.query(Topic).filter(Topic.topic_id.in_(payload.topic_ids)).all()
    if len(topics) != len(payload.topic_ids):
        found_ids = {topic.topic_id for topic in topics}
        missing = [topic_id for topic_id in payload.topic_ids if topic_id not in found_ids]
        raise HTTPException(status_code=400, detail=f"Missing topic IDs: {missing}")

    for topic in topics:
        if not topic.embedding:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"topic {topic.topic_id} has no embedding. Run POST /topics first "
                    "or ensure embedding was generated."
                ),
            )
        topic.embedding = json.loads(topic.embedding)

    resources = (
        db.query(Resource)
        .options(joinedload(Resource.authors))
        .filter(Resource.lifecycle_status == "active")
        .filter(Resource.embedding.is_not(None))
        .all()
    )
    if not resources:
        raise HTTPException(
            status_code=400,
            detail="No embedded resources found. Run POST /resources/embed first.",
        )

    for resource in resources:
        resource.embedding = json.loads(resource.embedding)

    matches = matcher.match_topics_to_resources(
        topics=topics,
        resources=resources,
        top_k=payload.top_k,
        min_score=payload.min_score,
    )

    return {
        "query_topics": [topic.topic_name for topic in topics],
        "total_resources_searched": len(resources),
        "results": matches,
    }
