# Academic RAG Assistant

A robust Retrieval-Augmented Generation (RAG) backend API built with **FastAPI**, **PostgreSQL with `pgvector`**, and **Ollama**. 

This system automates end-to-end document ingestion (supporting `.txt`, `.md`, and `.pdf`), token-based chunking with customizable overlap, vector embedding generation, cosine similarity retrieval, and LLM synthesis for context-grounded question answering.

---

## Key Features

- **FastAPI REST Web Service**: Asynchronous endpoints for file uploading, document ingestion, and context-based chat answering.
- **Multi-Format Document Ingestion**: Extensible `LoaderFactory` supporting plain text (`.txt`), Markdown (`.md`), and PDF (`.pdf`) documents.
- **Automated Text Cleaning**: Normalizes Unicode (NFKC), strips control characters and raw HTML, and standardizes whitespace before chunking.
- **Token-Based Chunking**: `TokenChunker` powered by `tiktoken` (`cl100k_base`) with configurable chunk size and overlap percentage.
- **PostgreSQL Vector Database**: Stores embeddings and performs similarity searches using `pgvector` (`<=>` cosine distance operator).
- **Local Ollama Integration**: Asynchronous clients for embedding generation (`nomic-embed-text`) and chat completion (`qwen2.5:0.5b`).
- **Rich Terminal Feedback**: Real-time progress visualization in terminal during ingestion using `rich`.

---

## Tech Stack & Dependencies

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **Language**: Python 3.14+
- **Environment & Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Database**: PostgreSQL 15+ with [`pgvector`](https://github.com/pgvector/pgvector) extension
- **LLM & Embeddings Provider**: [Ollama](https://ollama.com/)
- **Document Extractors**: `pypdf`, `beautifulsoup4`, `markdown`
- **Tokenization**: `tiktoken`
- **Config & Validation**: `pydantic`, `pydantic-settings`
- **Database Client**: `psycopg` (v3 async binary)
- **HTTP Client**: `httpx`
- **Terminal UI**: `rich`

---

## Project Structure

```
academic_rag_assistant/
├── app/
│   ├── main.py                  # FastAPI application entry point & router registration
│   ├── config.py                # Pydantic-settings configuration & database URL resolution
│   ├── database/
│   │   └── vector_db.py         # Async PostgreSQL connection manager (psycopg3)
│   ├── ingestion/
│   │   ├── loaders.py           # Document loaders (Text, Markdown, PDF) & LoaderFactory
│   │   ├── cleaner.py           # Text cleaning, Unicode normalization & artifact removal
│   │   ├── chunker.py           # Token-based text chunking using tiktoken
│   │   ├── pipeline.py          # Pipeline orchestrator (Load -> Clean -> Chunk)
│   │   └── storage.py           # Uploaded file persistence to storage directory
│   ├── repository/
│   │   └── documents.py         # Database CRUD & pgvector cosine similarity search
│   ├── routers/
│   │   ├── documents.py         # POST /document/save endpoint handler
│   │   └── question.py          # POST /question/chat endpoint handler
│   ├── schemas/
│   │   ├── document.py          # Pydantic schemas for document ingestion
│   │   └── question.py          # Pydantic schemas for RAG query request/response
│   └── services/
│       ├── embedding_service.py # Async client for Ollama embeddings API
│       ├── llm_service.py       # Async client for Ollama chat API
│       └── rag.py               # Core RAG workflow (Ingest, Search, Synthesis)
├── documents/                   # Uploaded & sample document storage directory
├── .env                         # Environment variables configuration file
├── pyproject.toml               # Project metadata & dependency definitions
├── uv.lock                      # Lockfile for reproducible environment state
└── README.md                    # Project documentation
```

---

## Prerequisites

1. **Python 3.14+**
2. **PostgreSQL** with `pgvector` extension enabled.
3. **Ollama** installed and running with target models pulled:
   ```bash
   ollama pull nomic-embed-text:latest
   ollama pull qwen2.5:0.5b
   ```

---

## Configuration (`.env`)

Create a `.env` file in the root directory:

```env
# PostgreSQL Configuration
DB_NAME=[DB_Name]
DB_USER=[DB_User]
DB_PASS=[DB_Password]
DB_HOST=[DB_Host]
DB_PORT=[DB_Port]

# Local Ollama AI Engine Settings
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=[Embedding_Model]
LARGE_LANGUAGE_MODEL=[LLM]
```

---

## Database Setup

Execute the following SQL commands on your PostgreSQL database to enable `pgvector` and create the necessary tables:

- Install pgvector from teh github repository and build it:

```bash
  # Install build tools and PostgreSQL development headers
  sudo apt update
  sudo apt install -y build-essential postgresql-server-dev-all git

  # Clone and build pgvector
  cd /tmp
  git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
  cd pgvector
  make
  sudo make install

```


```sql
-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    total_chunks INTEGER NOT NULL
);

-- Vector Chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR NOT NULL,
    metadata JSONB NOT NULL
);
```

---

## Installation & Running

1. **Install Dependencies**:
   Using `uv`:
   ```bash
   uv sync
   ```

2. **Start the FastAPI Application**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

3. **Access Interactive API Docs**:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

---

## REST API Reference

### 1. Root Health Check
- **Endpoint**: `GET /`
- **Description**: Returns welcome status message.
- **Response**:
  ```json
  {
    "message": "Welcome To RAG assistant"
  }
  ```

---

### 2. Document Upload & Ingestion
- **Endpoint**: `POST /document/save`
- **Content-Type**: `multipart/form-data`
- **Form Parameters**:
  - `file` (*UploadFile*, required): Document file (`.txt`, `.md`, `.pdf`).
  - `chunk_size` (*int*, optional): Target token count per chunk (default: `500`).
  - `overlap_size` (*float*, optional): Overlap fraction between consecutive chunks (default: `0.1`).
  - `subject` (*str*, optional): Subject tag for topic filtering (default: `""`).
  - `metadata` (*str*, optional): JSON string of custom metadata (default: `"{}"`).

- **Example `curl` Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/document/save" \
    -F "file=@documents/retriever_augmented_generation.md" \
    -F "chunk_size=500" \
    -F "overlap_size=0.1" \
    -F "subject=RAG" \
    -F 'metadata={"author": "AI Team"}'
  ```

- **HTTP Responses**:
  - `200 OK`: File processed and chunks stored successfully.
  - `409 Conflict`: File with identical filename already exists in the database.
  - `500 Internal Server Error`: Processing or storage failure.

---

### 3. RAG Chat & Retrieval
- **Endpoint**: `POST /question/chat`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "user_question": "What is Retrieval-Augmented Generation?"
  }
  ```

- **Example `curl` Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/question/chat" \
    -H "Content-Type: application/json" \
    -d '{"user_question": "What is Retrieval-Augmented Generation?"}'
  ```

- **Response Format**:
  ```json
  {
    "answer": "Retrieval-Augmented Generation (RAG) is an architectural framework...",
    "metadata": {
      "sources": [
        "retriever_augmented_generation.md"
      ],
      "subjects": [
        "RAG"
      ]
    }
  }
  ```

- **HTTP Responses**:
  - `200 OK`: Query processed successfully with context-grounded response.
  - `409 Conflict`: Ollama model failure or missing answer.

---

## Python Programmatic Usage

You can also run the core ingestion and RAG services directly within Python scripts:

```python
import asyncio
from pathlib import Path
from app.services.rag import insert_file, chat

async def main():
    # 1. Ingest a document directly
    doc_path = Path("documents/retriever_augmented_generation.md")
    await insert_file(
        file=doc_path,
        chunk_size=500,
        overlap_ratio=0.1,
        subject="AI & RAG",
        metadata={"author": "Rayen"}
    )

    # 2. Query the RAG system
    result = await chat("How does semantic chunking improve retrieval accuracy?")
    if result:
        print("Answer:\n", result["response"])
        print("Sources:", result["sources"])
        print("Subjects:", result["subjects"])

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Ingestion Pipeline Details

The document ingestion flow follows a three-stage pipeline:

1. **Loader Stage (`app/ingestion/loaders.py`)**:
   - Automatically selects the appropriate loader based on file extension (`.txt`, `.md`, `.pdf`).
   - Extracts raw string content from files. Markdown syntax is rendered to HTML and stripped of markup formatting via `BeautifulSoup`. PDF files are parsed page-by-page via `pypdf`.

2. **Cleaner Stage (`app/ingestion/cleaner.py`)**:
   - Performs Unicode normalization (`NFKC`).
   - Removes unprintable control characters.
   - Cleans HTML leftovers and section divider patterns (`---`, `***`, `===`).
   - Normalizes whitespace and paragraph gaps.

3. **Chunker Stage (`app/ingestion/chunker.py`)**:
   - Tokenizes clean text using `tiktoken` (`cl100k_base`).
   - Slices text into overlapping windows defined by `chunk_size` and `overlap_percentage`.
   - Generates chunk dictionaries containing text content, token count, and chunk index.
