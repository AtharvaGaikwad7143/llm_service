# LLM Service

A production-oriented AI backend built with **FastAPI, Google Gemini, PostgreSQL, pgvector, Docker, and AWS**.

The project evolves from a basic LLM API into a document-based **RAG (Retrieval-Augmented Generation)** system.

## Current Stage

The current implementation provides:

* Gemini-powered text generation
* Structured information extraction
* Pydantic request/response validation
* Request timeout handling
* Retry with exponential backoff
* Exception handling
* PDF text extraction
* Token-based document chunking
* Local sentence-transformer embeddings
* PostgreSQL + pgvector vector storage
* Cosine similarity search
* Metadata filtering
* Document ingestion API
* Semantic search API
* RAG question-answering API
* Retrieval evaluation with Recall@5
* Docker and Docker Compose
* AWS EC2 deployment
* Pytest API tests

## Architecture

```text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     FastAPI     │
                         └───────┬─────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
                  ▼              ▼              ▼
           /generate        /documents      /query
                  │              │              │
                  ▼              ▼              ▼
             Gemini API      PDF Parser     RAG Service
                                 │              │
                                 ▼              ▼
                              Chunking       Embedding
                                 │              │
                                 ▼              ▼
                           Embeddings      pgvector Search
                                                │
                                                ▼
                                           Context
                                                │
                                                ▼
                                             Gemini
                                                │
                                                ▼
                                         Answer + Sources
```

## RAG Pipeline

The current RAG flow is:

```text
PDF
 ↓
Text Extraction
 ↓
Token-based Chunking
 ↓
Sentence Transformer
 ↓
384-dimensional Embedding
 ↓
PostgreSQL + pgvector
 ↓
Cosine Similarity Search
 ↓
Top-K Relevant Chunks
 ↓
Context Construction
 ↓
Google Gemini
 ↓
Answer + Sources
```

## API

### Health Check

```http
GET /health
```

### Generate

```http
POST /generate
```

Request:

```json
{
  "prompt": "Explain Redis in one sentence."
}
```

### Extract

```http
POST /extract
```

Request:

```json
{
  "text": "Redis is an in-memory data store used for caching."
}
```

Response:

```json
{
  "title": "Redis Overview",
  "summary": "Redis is an in-memory data store.",
  "keywords": [
    "Redis",
    "caching"
  ]
}
```

### Upload Document

```http
POST /documents
```

Upload a PDF file using multipart form data.

The endpoint:

1. Validates the uploaded file.
2. Extracts text from the PDF.
3. Splits text into token-based chunks.
4. Generates embeddings.
5. Stores the document and chunks in PostgreSQL.
6. Stores embeddings in pgvector.

Example response:

```json
{
  "document_id": 7,
  "filename": "sample.pdf",
  "chunks_created": 9
}
```

### Search Documents

```http
POST /documents/search
```

Request:

```json
{
  "query": "What is Redis used for?",
  "limit": 5
}
```

The query is converted into an embedding and compared against stored document embeddings using cosine distance.

### Get Document

```http
GET /documents/{document_id}
```

Returns the stored document metadata and extracted content.

### RAG Query

```http
POST /query
```

Request:

```json
{
  "question": "What is Redis commonly used for?"
}
```

Response:

```json
{
  "answer": "Redis is an in-memory data store commonly used for caching and fast key-value operations.",
  "sources": [
    {
      "document_id": 1,
      "metadata": {
        "topic": "redis"
      }
    }
  ]
}
```

The LLM is instructed to answer using the retrieved context and to state when the available context is insufficient.

## Vector Search

The project uses:

* **Sentence Transformers** for local embeddings
* Model: `sentence-transformers/all-MiniLM-L6-v2`
* Embedding dimension: **384**
* PostgreSQL with **pgvector**
* Cosine distance for similarity search
* HNSW index for vector retrieval
* JSONB metadata filtering

The vector database schema contains:

```text
documents
├── id
├── filename
├── content
└── created_at

document_chunks
├── id
├── document_id
├── chunk_text
├── embedding
└── metadata
```

## Retrieval Evaluation

A retrieval evaluation dataset containing **20 questions** is included.

Evaluation checks whether the expected document appears in the top 5 retrieved results.

Current result:

```text
Correct: 20/20
Recall@5: 100.00%
```

The evaluation runs locally and does **not require Gemini API calls**.

Run:

```bash
python -m scripts.evaluate_rag
```

## Tech Stack

* Python
* FastAPI
* Pydantic
* Google Gemini API
* Sentence Transformers
* NumPy
* PostgreSQL
* pgvector
* SQLAlchemy
* PyMuPDF
* Docker
* Docker Compose
* AWS EC2
* Pytest
* Git / GitHub

## Project Structure

```text
llm-service/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── documents.py
│   │       └── query.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── init.sql
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── pdf_parser.py
│   │   └── tokenizer.py
│   │
│   ├── repositories/
│   │   ├── document_repository.py
│   │   └── vector_repository.py
│   │
│   └── services/
│       ├── document_service.py
│       ├── embeddings.py
│       ├── llm.py
│       └── rag_service.py
│
├── scripts/
│   ├── evaluate_rag.py
│   ├── rag_eval_questions.json
│   └── development/evaluation scripts
│
├── tests/
│   └── test_api.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Running Locally

Create `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/llm_service
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run PostgreSQL + pgvector:

```bash
docker compose up -d db
```

Run the API:

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Docker

Build and start the complete stack:

```bash
docker compose up -d --build
```

Services:

```text
FastAPI
PostgreSQL + pgvector
```

Check containers:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs api
```

## Testing

Run API tests:

```bash
pytest -q
```

Current API test coverage includes:

* Health endpoint
* Generate request validation
* Extract request validation
* Query request validation

Run retrieval evaluation:

```bash
python -m scripts.evaluate_rag
```

## Environment Variables

Secrets are provided through environment variables.

`.env` is intentionally excluded from Git.

Never commit:

```text
.env
*.pem
AWS credentials
API keys
```

Use `.env.example` as the template for required configuration.

## Development Direction

The system is being developed incrementally toward a production-oriented AI backend:

```text
LLM APIs
   ↓
Embeddings
   ↓
Vector Search
   ↓
PostgreSQL + pgvector
   ↓
Document Ingestion
   ↓
RAG
   ↓
Production RAG
   ↓
Async AI Processing
   ↓
Tool Calling
   ↓
Observability
   ↓
ML / MLOps
   ↓
Cloud + Kubernetes
```

Future improvements include hybrid search, reranking, streaming responses, RAG evaluation improvements, async AI processing, tool calling, observability, ML serving, and cloud infrastructure.

## Author

**Atharva Gaikwad**

GitHub: `https://github.com/AtharvaGaikwad7143`
