# Local RAG Knowledge Assistant

![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite)

Upload notes and documents, chunk them into searchable passages, then ask questions and get answers with source citations. Runs entirely locally — no API keys, no cloud.

## Features

- Upload plain-text documents or paste notes directly
- Automatic text chunking with configurable overlap
- Keyword-based passage retrieval with BM25 scoring
- Q&A with source citations showing which chunk produced the answer
- SQLite-backed document and chunk storage
- All processing stays on your machine

## Tech Stack

- Python 3.11+ / FastAPI / SQLite
- Vanilla HTML/CSS/JS frontend served by the API
- Pytest

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8103
```

Open: http://localhost:8103

Windows: double-click `run.bat`

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Browser demo UI |
| GET | `/api/health` | Health check |
| GET | `/docs` | Interactive API docs |

## Tests

```bash
uv run pytest -q
```
