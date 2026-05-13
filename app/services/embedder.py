from __future__ import annotations

import json
import os

from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model


def embed_text(text: str) -> list[float]:
    """Embed a single string. Returns list of 384 floats."""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def build_resource_text(
    title: str, description: str | None, subject_tags: list[str] | None
) -> str:
    parts = [title]
    if description:
        parts.append(description)
    if subject_tags:
        parts.append(" ".join(subject_tags))
    return ". ".join(part.strip() for part in parts if part and part.strip())


def build_topic_text(topic_name: str, topic_description: str | None) -> str:
    parts = [topic_name]
    if topic_description:
        parts.append(topic_description)
    return ". ".join(part.strip() for part in parts if part and part.strip())


def embed_resource(resource) -> list[float]:
    text = build_resource_text(resource.title, resource.description, None)
    return embed_text(text)


def embed_topic(topic) -> list[float]:
    text = build_topic_text(topic.topic_name, topic.topic_description)
    return embed_text(text)


def serialize_embedding(embedding: list[float]) -> str:
    return json.dumps(embedding)


def deserialize_embedding(embedding: str | None) -> list[float] | None:
    if not embedding:
        return None
    return json.loads(embedding)
