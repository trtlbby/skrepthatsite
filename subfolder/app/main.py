from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from subfolder.app.database import Base, engine
from subfolder.app.routers import topics
from subfolder.app.routers import crawl, match, resources

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Module 3 - OER Intelligent Scraping Service (PoC)",
    description="Scrapes OER platforms, normalizes metadata, generates embeddings, and matches resources to course topics.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router, prefix="/topics", tags=["Topics"])
app.include_router(crawl.router, prefix="/crawl", tags=["Crawl"])
app.include_router(resources.router, prefix="/resources", tags=["Resources"])
app.include_router(match.router, prefix="/match", tags=["Match"])


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "oer-poc"}
