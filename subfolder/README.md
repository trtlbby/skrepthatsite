# Module 3 - OER Intelligent Scraping Service (PoC)

This backend-only proof of concept scrapes Open Educational Resource platforms, normalizes
resource metadata, generates vector embeddings, and matches resources to course topics using
semantic similarity. It is designed to be a lightweight bridge to a production PostgreSQL +
pgvector implementation later.

## Setup

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run the API:

```
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

## Environment Variables

- `DATABASE_URL`: SQLAlchemy database URL (SQLite for this PoC)
- `MERLOT_API_KEY`: API key for MERLOT (optional for the PoC)
- `EMBED_MODEL`: SentenceTransformers model name (default is `all-MiniLM-L6-v2`)

## Demo Workflow

Step 1 - Seed topics manually
POST /topics
{
  "topic_name": "Finite Automata",
  "topic_description": "Study of deterministic and nondeterministic finite automata, state transitions, and regular language acceptance.",
  "source_module": "manual"
}

POST /topics
{
  "topic_name": "Turing Machines",
  "topic_description": "Formal model of computation, tape operations, halting problem, and computability theory.",
  "source_module": "manual"
}

POST /topics
{
  "topic_name": "Context-Free Grammars",
  "topic_description": "Production rules, parse trees, pushdown automata equivalence, and CYK algorithm.",
  "source_module": "manual"
}

Step 2 - Crawl OER sources
POST /crawl  { "platform": "openstax", "limit": 50 }
POST /crawl  { "platform": "gutenberg", "limit": 50 }
POST /crawl  { "platform": "merlot", "limit": 50 }  - skips gracefully if no API key

Step 3 - Generate resource embeddings
POST /resources/embed

Step 4 - Run matching
POST /match
{
  "topic_ids": ["<id1>", "<id2>", "<id3>"],
  "top_k": 10,
  "min_score": 0.3
}

Step 5 - Inspect results
GET /resources?platform=openstax
GET /resources/{resource_id}

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | /health | Service health check |
| POST | /topics | Create a topic and generate embedding |
| GET | /topics | List topics |
| DELETE | /topics/{topic_id} | Delete topic |
| POST | /crawl | Crawl a source platform and ingest resources |
| GET | /resources | List resources (optional platform filter) |
| GET | /resources/{resource_id} | Get one resource |
| POST | /resources/embed | Generate embeddings for resources |
| DELETE | /resources/{resource_id} | Archive a resource |
| POST | /match | Match topics to resources |

## Notes on PostgreSQL + pgvector Migration

- Swap `DATABASE_URL` to a PostgreSQL URL and update SQLAlchemy engine settings.
- Replace JSON string embeddings with a pgvector column and remove manual JSON serialization.
- Move cosine similarity computation into SQL queries using pgvector operators.
