# Local RAG Knowledge Assistant

![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite)
![Ollama](https://img.shields.io/badge/Ollama-optional-000?style=flat-square&logo=ollama)

Upload notes and documents, chunk them into searchable passages, then ask questions and get answers with source citations. Runs entirely locally — no cloud, no API keys.

Uses **Ollama embeddings** (nomic-embed-text) for cosine-similarity retrieval and **Ollama LLM** (llama3.2) for answer generation when available. Falls back to keyword overlap when Ollama is offline.

## Features

- Upload plain-text documents or paste notes directly
- Automatic text chunking with configurable overlap
- **Embedding-based retrieval** via Ollama nomic-embed-text (falls back to keyword matching)
- **LLM-powered answer generation** via Ollama llama3.2 (falls back to excerpt concatenation)
- Source citations showing which chunk produced the answer
- SQLite-backed document and chunk storage
- All data stays on your machine

## Tech Stack

- Python 3.11+ / FastAPI / SQLite
- Ollama (optional — for embeddings + LLM)
- Vanilla HTML/CSS/JS frontend served by the API
- Pytest

## Quick Start

```bash
# Basic (keyword-only, no Ollama needed)
uv sync
uv run uvicorn src.main:app --reload --port 8103

# With Ollama (requires running Ollama server)
ollama pull nomic-embed-text
ollama pull llama3.2:3b
uv sync
uv run uvicorn src.main:app --reload --port 8103
```

Open: http://localhost:8103

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Browser demo UI |
| GET | `/api/health` | Health check (includes ollama_available flag) |
| POST | `/api/ingest` | Ingest text as chunks (stores embeddings if Ollama available) |
| POST | `/api/ask` | Ask a question against ingested chunks |
| GET | `/docs` | Interactive API docs |

## Tests

```bash
uv run pytest -q
```

## Ollama Setup

1. Install Ollama: https://ollama.com/download
2. Pull the models:
   ```bash
   ollama pull nomic-embed-text
   ollama pull llama3.2:3b
   ```
3. Ensure Ollama is running (`ollama serve` or system tray app)
4. Install with Ollama extras: `pip install ollama`
5. The health endpoint reports `ollama_available: true` when everything is connected
