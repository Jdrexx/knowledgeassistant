# Local RAG Knowledge Assistant

![Python](https://img.shields.io/badge/Python-3.11_|_3.12-3776AB?style=flat-square&logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite) ![RAG](https://img.shields.io/badge/RAG-7C3AED?style=flat-square) ![Chunking](https://img.shields.io/badge/Chunking-0EA5E9?style=flat-square)

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
