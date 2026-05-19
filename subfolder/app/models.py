from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from subfolder.app.database import Base


class Resource(Base):
    __tablename__ = "resources"

    resource_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String, nullable=True)
    source_platform: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str | None] = mapped_column(String, nullable=True)
    doi: Mapped[str | None] = mapped_column(String, nullable=True)
    license_type: Mapped[str | None] = mapped_column(String, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(String, default="active")
    date_ingested: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    duplicate_source_ids: Mapped[str | None] = mapped_column(Text, nullable=True)

    authors: Mapped[list["ResourceAuthor"]] = relationship(
        "ResourceAuthor",
        back_populates="resource",
        cascade="all, delete-orphan",
    )


class ResourceAuthor(Base):
    __tablename__ = "resource_authors"

    author_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    resource_id: Mapped[str] = mapped_column(String, ForeignKey("resources.resource_id"), nullable=False)
    author_name: Mapped[str] = mapped_column(String, nullable=False)

    resource: Mapped[Resource] = relationship("Resource", back_populates="authors")


class Topic(Base):
    __tablename__ = "topics"

    topic_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    topic_name: Mapped[str] = mapped_column(String, nullable=False)
    topic_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_module: Mapped[str] = mapped_column(String, default="manual")
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    platform: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="running")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
