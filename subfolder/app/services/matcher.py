from __future__ import annotations

from datetime import datetime

import numpy as np


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors. Returns float 0.0-1.0."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def match_topics_to_resources(
    topics: list,
    resources: list,
    top_k: int = 10,
    min_score: float = 0.3,
) -> list[dict]:
    results: list[dict] = []
    current_year = datetime.utcnow().year

    for resource in resources:
        if not resource.embedding:
            continue

        per_topic_scores: dict[str, float] = {}
        scores: list[float] = []

        for topic in topics:
            if not topic.embedding:
                continue
            score = cosine_similarity(topic.embedding, resource.embedding)
            per_topic_scores[topic.topic_name] = round(score, 4)
            scores.append(score)

        if not scores:
            continue

        base_score = sum(scores) / len(scores)
        recency_boost = (
            0.05
            if resource.publication_year and resource.publication_year >= (current_year - 5)
            else 0.0
        )
        quality_factor = resource.quality_score if resource.quality_score is not None else 0.5
        final_score = round((base_score + recency_boost) * quality_factor, 4)

        if final_score < min_score:
            continue

        results.append(
            {
                "resource_id": resource.resource_id,
                "title": resource.title,
                "url": resource.url,
                "source_platform": resource.source_platform,
                "publication_year": resource.publication_year,
                "authors": [author.author_name for author in resource.authors],
                "final_score": final_score,
                "per_topic_scores": per_topic_scores,
                "quality_score": resource.quality_score,
            }
        )

    results.sort(key=lambda item: item["final_score"], reverse=True)
    return results[:top_k]
