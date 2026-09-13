# LLM Service

A production-oriented AI backend built with **FastAPI, Google Gemini, PostgreSQL, Redis, Docker, and AWS**.

This project is being developed incrementally as a full-stack AI backend system, starting with LLM APIs and evolving toward a production-grade **RAG and AI knowledge platform**.

## Current Stage

The current implementation provides:

* Gemini-powered text generation
* Structured information extraction
* Pydantic request/response validation
* Request timeout handling
* Retry with exponential backoff
* Logging and exception handling
* Docker and Docker Compose
* AWS EC2 deployment

## Architecture

```text
Client
  |
  v
FastAPI
  |
  v
LLM Service
  |
  v
Google Gemini
```

The current application runs as a Docker container and has been deployed to AWS EC2.

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
  "text": "Redis is an in-memory data store used for caching and real-time applications."
}
```

Response follows a validated structured schema:

```json
{
  "title": "Redis Overview",
  "summary": "Redis is an in-memory data store...",
  "keywords": [
    "Redis",
    "caching",
    "real-time applications"
  ]
}
```

## Tech Stack

* Python
* FastAPI
* Pydantic
* Google Gemini API
* PostgreSQL
* pgvector
* Redis
* Celery
* Docker
* AWS
* GitHub Actions
* Pytest

> Some technologies listed above will be introduced as the project evolves.

## Project Structure

```text
llm-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   └── services/
├── tests/
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
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Docker

Build:

```bash
docker build -t llm-service .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env llm-service
```

Or with Compose:

```bash
docker compose up -d --build
```

## Testing

```bash
pytest
```

## Development Direction

The system will evolve from a basic LLM API into a production-oriented AI backend with:

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
Async Processing
   ↓
Tool Calling
   ↓
Observability
   ↓
ML / MLOps
   ↓
Cloud + Kubernetes
```

The README will be updated as major capabilities are added.

## Security

Secrets such as API keys are stored through environment variables and are not committed to the repository.

Never commit:

```text
.env
*.pem
AWS credentials
API keys
```

## Author

**Atharva Gaikwad**

GitHub: https://github.com/AtharvaGaikwad7143
