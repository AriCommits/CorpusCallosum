# CorpusCallosum

Local-first RAG service for personal knowledge management.

## Quick Start (30 seconds)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Copy config
cp configs/corpus_callosum.yaml.example configs/corpus_callosum.yaml

# 3. Start Ollama (if not running)
ollama serve && ollama pull llama3
```

## Basic Usage (CLI)

```bash
# Ingest documents
corpus-ingest --path ./vault/my-notes --collection notes

# Ask a question
corpus-ask "What is photosynthesis?" --collection notes

# Generate flashcards
corpus-flashcards --collection notes

# List collections
corpus-collections
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `corpus-ingest --path <path> --collection <name>` | Ingest documents |
| `corpus-ask "<question>" --collection <name>` | Ask a question |
| `corpus-flashcards --collection <name>` | Generate flashcards |
| `corpus-collections` | List all collections |
| `corpus-api` | Start the REST API server |

### CLI Options

```bash
# corpus-ask
corpus-ask "question" -c collection      # Short form
corpus-ask -q "question" -c collection   # Alternative
corpus-ask "question" -c col -m mistral  # Override model
corpus-ask "question" -c col -s session1 # Multi-turn conversation

# corpus-flashcards
corpus-flashcards -c collection              # Print to stdout
corpus-flashcards -c collection -o cards.txt # Save to file

# corpus-collections
corpus-collections         # Plain list
corpus-collections --json  # JSON output
```

## Features

- Hybrid retrieval (semantic + BM25 + RRF fusion)
- Supports PDF, Markdown, TXT files
- Multi-turn conversations with session memory
- Flashcard generation and writing critique
- Rate limiting and API key authentication
- OpenTelemetry observability (optional)

## REST API

Start the server with `corpus-api`, then access `http://localhost:8080`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ingest` | POST | Ingest documents into a collection |
| `/query` | POST | Query with RAG (SSE stream) |
| `/critique` | POST | Get writing feedback (SSE stream) |
| `/flashcards` | POST | Generate study flashcards (SSE stream) |
| `/summarize` | POST | Summarize a collection |
| `/collections` | GET | List all collections |
| `/rate-limit` | GET | Check rate limit status |

API docs available at `/docs` (Swagger) and `/redoc`.

## Configuration

Config is loaded from `configs/corpus_callosum.yaml` or `CORPUS_CALLOSUM_CONFIG` env var.

Key settings:

```yaml
model:
  endpoint: http://localhost:11434  # Ollama endpoint
  name: llama3                       # Model name
  backend: ollama                    # ollama, openai, or anthropic

server:
  host: 127.0.0.1
  port: 8080

security:
  rate_limit_enabled: true
  auth_enabled: true
  api_keys: []  # SHA-256 hashed API keys
```

## API Authentication

When `auth_enabled: true`, include your API key:

```bash
curl -H "X-API-Key: your-key" http://localhost:8080/health
```

## Docker

```bash
cp configs/corpus_callosum.docker.yaml.example configs/corpus_callosum.docker.yaml
docker compose -f .docker/docker-compose.yml up --build
```

Includes ChromaDB, OpenTelemetry Collector, and Jaeger at `http://localhost:16686`.

## Project Structure

```
src/corpus_callosum/
  cli.py          # CLI commands (ask, flashcards, collections)
  api.py          # FastAPI REST endpoints
  agent.py        # RAG orchestration
  retriever.py    # Hybrid search (semantic + BM25)
  ingest.py       # Document ingestion
  config.py       # Configuration
  llm_backends.py # Multi-provider LLM support
  security.py     # Rate limiting, auth
  observability.py # OpenTelemetry tracing
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
```

## Troubleshooting

**Ollama not running**: Start with `ollama serve` and pull a model: `ollama pull llama3`

**Config not found**: Copy the example: `cp configs/corpus_callosum.yaml.example configs/corpus_callosum.yaml`

**Observability errors**: Install optional deps: `pip install corpus-callosum[observability]`
