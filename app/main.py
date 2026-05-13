from fastapi import FastAPI

from app.database import Base, engine
from app.routers import crawl, match, resources, topics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Module 3 - OER Intelligent Scraping Service (PoC)",
    description="Scrapes OER platforms, normalizes metadata, generates embeddings, and matches resources to course topics.",
    version="0.1.0",
)

app.include_router(topics.router, prefix="/topics", tags=["Topics"])
app.include_router(crawl.router, prefix="/crawl", tags=["Crawl"])
app.include_router(resources.router, prefix="/resources", tags=["Resources"])
app.include_router(match.router, prefix="/match", tags=["Match"])


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "oer-poc"}
