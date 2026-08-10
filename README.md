# Education RAG System

A Retrieval-Augmented Generation (RAG) proof-of-concept built with PostgreSQL, vector embeddings, and Ollama. This project ingests text, markdown, and PDF documents, chunking and embedding document passages for semantic search and LLM-powered responses.

## Project Overview

- `main.py` orchestrates document ingestion, semantic search, and LLM query generation.
- `config.py` loads environment configuration using `pydantic-settings`.
- `database/vector_db.py` provides an async PostgreSQL connection helper.
- `repository/documents.py` stores documents and chunks, and performs vector search.
- `ingestion/` contains loaders, text cleaning, and chunking logic.
- `services/` defines embedding and LLM API clients for Ollama.
- `documents/` contains sample document files.

## Requirements

- Python 3.14+
- PostgreSQL with `pgvector` support
- Ollama running locally or accessible via API

Python dependencies from `pyproject.toml`:

- beautifulsoup4
- httpx
- markdown
- ollama
- psycopg[binary]
- pydantic
- pydantic-settings
- pypdf
- rich
- tiktoken

## Installation

1. Create and activate a Python virtual environment:

- Install uv tool if not installed

```bash
sudo apt install uv
```

2. Install dependencies using `uv` for sync environment management:

```bash
uv sync
```


## Configuration

Create a `.env` file in the project root with your database and Ollama settings, for example:

- For example
```env
DB_NAME=postgres
DB_USER=postgres
DB_PASS=rayen
DB_HOST=127.0.0.1
DB_PORT=5432
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text:latest
LARGE_LANGUAGE_MODEL=qwen2.5:0.5b
```

## Database Setup

This project expects PostgreSQL tables named `documents` and `chunks`.

Example SQL schema:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_type TEXT NOT NULL,
  total_chunks INTEGER NOT NULL
);

CREATE TABLE chunks (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id),
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR NOT NULL,
  metadata JSONB NOT NULL
);
```

## Usage

### Run the main program

- Select the funtion taht you want to run in main function in main.py file and don't forget await keyword
- Then run this command
```bash
uv run main.py
```

By default, `main.py` runs a simple RAG prompt flow:

- embeds a query
- retrieves top-ranked chunks from the vector store
- sends the retrieved context to the Ollama chat endpoint

### Ingest a document

Use the `insert_file` function in `main.py` to add a document to the database:

```python
from pathlib import Path
import asyncio
from main import insert_file

asyncio.run(insert_file(Path("documents/retriever_augmented_generation.md"), chunk_size=500, overlap_ratio=0.1, subject="RAG"))
```

### Search and chat

The `chat()` function in `main.py` performs semantic retrieval and sends the combined context to the configured LLM.

## Project Structure

- `config.py` — environment-aware settings and DB connection string
- `main.py` — ingestion and RAG execution
- `database/vector_db.py` — async DB connection helper
- `repository/documents.py` — CRUD and vector search operations
- `ingestion/loaders.py` — file loaders for `.txt`, `.md`, and `.pdf`
- `ingestion/cleaner.py` — text normalization and cleaning
- `ingestion/chunker.py` — token-based chunking with overlap
- `services/embedding_service.py` — Ollama embedding API client
- `services/llm_service.py` — Ollama chat API client

## Notes

- The embedding service expects Ollama to provide the configured embedding model.
- The vector search uses PostgreSQL vector comparisons with `embedding <=> %s::vector`.
- Ensure the database is reachable and the `pgvector` extension is installed.


