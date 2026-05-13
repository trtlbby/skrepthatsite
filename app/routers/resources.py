from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Resource
from app.schemas import ResourceResponse
from app.services import embedder

router = APIRouter()


@router.get("", response_model=list[ResourceResponse])
def list_resources(
    platform: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Resource).options(joinedload(Resource.authors))
    if platform:
        query = query.filter(Resource.source_platform == platform)
    return query.offset(offset).limit(limit).all()


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    resource = (
        db.query(Resource)
        .options(joinedload(Resource.authors))
        .filter(Resource.resource_id == resource_id)
        .first()
    )
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("/embed")
def embed_resources(db: Session = Depends(get_db)):
    embedded = 0
    skipped = 0

    while True:
        batch = (
            db.query(Resource)
            .options(joinedload(Resource.authors))
            .filter(Resource.embedding.is_(None))
            .limit(50)
            .all()
        )
        if not batch:
            break

        for resource in batch:
            if not resource.title:
                skipped += 1
                continue
            embedding = embedder.embed_resource(resource)
            resource.embedding = embedder.serialize_embedding(embedding)
            embedded += 1

        db.commit()

    return {
        "embedded": embedded,
        "skipped": skipped,
        "message": "embeddings generated",
    }


@router.delete("/{resource_id}")
def archive_resource(resource_id: str, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.lifecycle_status = "archived"
    db.commit()
    return {"message": "archived", "resource_id": resource_id}
