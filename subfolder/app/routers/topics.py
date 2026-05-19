from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from subfolder.app.database import get_db
from subfolder.app.models import Topic
from subfolder.app.schemas import TopicCreate, TopicResponse
from subfolder.app.services import embedder

router = APIRouter()


@router.post("", response_model=TopicResponse)
def create_topic(payload: TopicCreate, db: Session = Depends(get_db)):
    topic = Topic(
        topic_name=payload.topic_name,
        topic_description=payload.topic_description,
        source_module=payload.source_module,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    embedding = embedder.embed_topic(topic)
    topic.embedding = embedder.serialize_embedding(embedding)
    db.commit()
    db.refresh(topic)

    return topic


@router.get("", response_model=list[TopicResponse])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).order_by(Topic.created_at.desc()).all()


@router.delete("/{topic_id}")
def delete_topic(topic_id: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db.delete(topic)
    db.commit()
    return {"message": "deleted", "topic_id": topic_id}
