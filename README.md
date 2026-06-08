# Local RAG Knowledge Assistant

Upload notes/docs, chunk them, search relevant passages, and answer questions with citations.

## Why this project exists

This is a portfolio-ready MVP in the **private knowledge search** lane. It demonstrates practical API product thinking, clean documentation, tests, and a working local browser demo.

## Features

- Document ingestion
- Chunked keyword retrieval
- Question answering with citations
- Local-first architecture
- SQLite-backed document store

## Tech Stack

- Python 3.11+
- FastAPI
- SQLite
- Vanilla HTML/CSS/JS frontend served by the API
- Pytest API tests

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8103
```

Then open: http://localhost:8103

Windows one-click launcher: `run.bat`

## API

- `GET /` - browser demo
- `GET /api/health` - health check
- `GET /docs` - interactive FastAPI docs

## Verification

```bash
uv run pytest -q
```

## Roadmap

- Add authenticated user accounts
- Add production deployment config
- Replace deterministic helper logic with local Ollama model calls where useful
- Add screenshots and a short demo GIF
