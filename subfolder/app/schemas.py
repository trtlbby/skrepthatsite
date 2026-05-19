from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ResourceAuthorSchema(BaseModel):
    author_id: str
    author_name: str


class ResourceResponse(BaseModel):
    resource_id: str
    title: str
    description: str | None
    publication_year: int | None
    source_type: str | None
    source_platform: str
    url: str
    isbn: str | None
    doi: str | None
    license_type: str | None
    lifecycle_status: str
    date_ingested: datetime
    quality_score: float | None
    authors: list[ResourceAuthorSchema]

    model_config = ConfigDict(from_attributes=True)


class TopicCreate(BaseModel):
    topic_name: str
    topic_description: str | None = None
    source_module: str = "manual"


class TopicResponse(BaseModel):
    topic_id: str
    topic_name: str
    topic_description: str | None
    source_module: str
    created_at: datetime
    embedding: str | None = Field(default=None, exclude=True)

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def has_embedding(self) -> bool:
        return self.embedding is not None


class CrawlRequest(BaseModel):
    platform: Literal["openstax", "gutenberg", "merlot"]
    limit: int = 50


class CrawlResponse(BaseModel):
    log_id: str
    platform: str
    records_fetched: int
    records_inserted: int
    records_skipped: int
    status: str
    error_message: str | None


class MatchRequest(BaseModel):
    topic_ids: list[str]
    top_k: int = 10
    min_score: float = 0.3


class ResourceMatchResult(BaseModel):
    resource_id: str
    title: str
    url: str
    source_platform: str
    publication_year: int | None
    authors: list[str]
    final_score: float
    per_topic_scores: dict[str, float]
    quality_score: float | None


class MatchResponse(BaseModel):
    query_topics: list[str]
    total_resources_searched: int
    results: list[ResourceMatchResult]
