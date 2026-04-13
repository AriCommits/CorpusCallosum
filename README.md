# CorpusCallosum

**Unified Learning & Knowledge Management Toolkit**

A modular, AI-powered system for personal knowledge management with RAG (Retrieval-Augmented Generation), flashcard generation, video transcription, and intelligent study workflows.

## Features

### Core Tools
- **RAG Agent**: Query your personal knowledge base with intelligent context-aware responses
- **Flashcard Generator**: Create study cards from your documents with AI-powered Q&A generation
- **Summary Generator**: Generate comprehensive summaries with key insights and outlines
- **Quiz Generator**: Build interactive quizzes with multiple choice, true/false, and short answer questions
- **Video Transcriber**: Convert lectures and videos to searchable text with AI-powered cleaning and augmentation

### Advanced Features
- **Multi-LLM Backend Support**: Ollama, OpenAI-compatible, and Anthropic-compatible APIs
- **MCP Server Integration**: All tools accessible via Model Context Protocol for agent orchestration
- **Dual Interface**: Every tool works standalone via CLI or through MCP for agent workflows
- **Unified Database**: Single ChromaDB instance with intelligent collection management
- **Pre-Built Orchestrations**: Study sessions, lecture processing pipelines, and knowledge base workflows
- **Secrets & Key Management**: Secure keyring-backed storage for API keys and credentials

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/CorpusCallosum.git
cd CorpusCallosum

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install corpus-callosum
```

### Basic Configuration

1. **Copy base configuration**:
   ```bash
   cp configs/base.yaml my-config.yaml
   ```

2. **Edit configuration** for your LLM setup:
   ```yaml
   llm:
     endpoint: http://localhost:11434  # Ollama endpoint
     model: llama3                     # Your preferred model
     temperature: 0.7
   
   database:
     mode: persistent
     persist_directory: ./chroma_store
   ```

3. **Start your LLM backend** (e.g., Ollama):
   ```bash
   ollama serve
   ollama pull llama3
   ```

## Usage

### Unified CLI (recommended)

All tools are available under a single `corpus` command that works identically on Windows (PowerShell), macOS, and Linux:

```bash
corpus --help                    # show all subcommands
corpus --version
```

#### RAG

```bash
corpus rag ingest ./documents --collection notes
corpus rag query "What is machine learning?" --collection notes
corpus rag chat --collection notes           # interactive session
```

#### Flashcards, Summaries, Quizzes

```bash
corpus flashcards --collection notes --count 15 --difficulty intermediate
corpus summaries  --collection notes --length medium
corpus quizzes    --collection notes --count 10
```

#### Video Processing

```bash
corpus video transcribe ./lectures/ --course BIOL101 --lecture 1
corpus video clean transcript.md
corpus video augment transcript.md --auto
corpus video pipeline ./lectures/ --course BIOL101 --lecture 1  # full pipeline
```

#### Orchestrations

```bash
corpus orchestrate study-session    --collection notes --topic "databases"
corpus orchestrate lecture-pipeline ./lecture.mp4 --course CS101 --lecture 3
corpus orchestrate build-kb         ./documents --collection kb
corpus orchestrate query-kb         --collection kb "Explain neural networks"
```

#### Developer Tools

These replace shell scripts and work cross-platform:

```bash
corpus dev setup       # pip install -e .[dev]
corpus dev test        # run pytest
corpus dev test --cov  # run pytest with coverage
corpus dev lint        # ruff check + mypy
corpus dev fmt         # ruff format
corpus dev build       # build distribution package
corpus dev clean       # remove __pycache__, build artifacts

# Shell completion (add output to your shell profile)
corpus dev completion bash        # bash
corpus dev completion zsh         # zsh
corpus dev completion fish        # fish
corpus dev completion powershell  # PowerShell
```

---

### Individual entry points (backwards-compatible)

The legacy `corpus-*` commands remain available:

```bash
# RAG queries
corpus-rag ingest --path ./documents --collection notes
corpus-rag query --collection notes --query "What is machine learning?"
corpus-rag chat --collection notes

# Generate flashcards
corpus-flashcards --collection notes --count 15 --difficulty intermediate

# Create summaries
corpus-summaries --collection notes --topic "artificial intelligence"

# Build quizzes
corpus-quizzes --collection notes --difficulty advanced --count 10

# Transcribe and process videos
corpus-video transcribe ./lectures/ --course BIOL101 --lecture 1
corpus-video clean transcript.md
corpus-video augment transcript.md
corpus-video pipeline ./lectures/ --course BIOL101 --lecture 1

# Run pre-composed workflows
corpus-orchestrate study-session --collection notes --topic "databases"
corpus-orchestrate lecture-pipeline lecture.mp4 --course CS101 --lecture 3
corpus-orchestrate build-kb ./documents --collection kb
corpus-orchestrate query-kb --collection kb "Explain neural networks"
```

### Database Management

```bash
corpus-db list
corpus-db backup notes --output ./backups/notes.tar.gz
corpus-db restore ./backups/notes.tar.gz
corpus-db backup-all --output-dir ./backups/
corpus-db export notes --output notes.json --format json
corpus-db migrate old_collection new_collection
```

### Secrets & API Key Management

```bash
# Secrets (backed by system keyring)
corpus-secrets store OPENAI_API_KEY
corpus-secrets get   OPENAI_API_KEY
corpus-secrets list
corpus-secrets delete OPENAI_API_KEY
corpus-secrets migrate           # import from environment variables
corpus-secrets validate          # check required secrets are set

# MCP server API keys
corpus-api-keys generate my-agent
corpus-api-keys list
corpus-api-keys revoke <key>
corpus-api-keys test   <key>
```

### MCP Server (Agent Integration)

```bash
corpus-mcp-server                # runs on http://localhost:8000/mcp
```

Configure your AI agent to connect and call tools like:
- `generate_flashcards(collection="notes", count=10)`
- `rag_query(collection="notes", query="Explain quantum computing")`
- `transcribe_video(video_path="lecture.mp4", clean=True)`

## CLI Reference

### Unified `corpus` command

| Subcommand | Description |
|---|---|
| `corpus rag` | RAG agent: `ingest`, `query`, `chat` |
| `corpus flashcards` | Generate flashcards from a collection |
| `corpus summaries` | Generate summaries from a collection |
| `corpus quizzes` | Generate quizzes from a collection |
| `corpus video` | Video processing: `transcribe`, `clean`, `augment`, `pipeline` |
| `corpus orchestrate` | Workflows: `study-session`, `lecture-pipeline`, `build-kb`, `query-kb` |
| `corpus dev` | Developer tools: `setup`, `test`, `lint`, `fmt`, `build`, `clean`, `completion` |

### Legacy `corpus-*` entry points

| Command | Description |
|---|---|
| `corpus-rag` | RAG agent: `ingest`, `query`, `chat` |
| `corpus-flashcards` | Generate flashcards |
| `corpus-summaries` | Generate summaries |
| `corpus-quizzes` | Generate quizzes |
| `corpus-video` | Video processing: `transcribe`, `clean`, `augment`, `pipeline` |
| `corpus-orchestrate` | Workflows: `study-session`, `lecture-pipeline`, `build-kb`, `query-kb` |
| `corpus-db` | Database: `list`, `backup`, `restore`, `backup-all`, `export`, `migrate` |
| `corpus-secrets` | Secrets: `store`, `get`, `list`, `delete`, `migrate`, `validate` |
| `corpus-api-keys` | API keys: `generate`, `list`, `revoke`, `test` |
| `corpus-mcp-server` | Start the MCP server |

## Project Structure

```
CorpusCallosum/
├── src/                          # All source packages (package-dir = src)
│   ├── config/                   # Configuration management (loader, schema)
│   ├── db/                       # Database layer (ChromaDB, management CLI)
│   ├── llm/                      # LLM backend abstraction (Ollama, OpenAI, Anthropic)
│   ├── mcp_server/               # MCP server implementation
│   ├── orchestrations/           # Pre-composed workflows + CLI
│   ├── tools/                    # Individual tool implementations
│   │   ├── rag/                  # RAG agent (ingest, query, chat)
│   │   ├── flashcards/           # Flashcard generation
│   │   ├── summaries/            # Summary generation
│   │   ├── quizzes/              # Quiz generation
│   │   └── video/                # Video transcription, cleaning, augmentation
│   ├── utils/                    # Shared utilities
│   │   ├── auth.py               # MCP server authentication
│   │   ├── manage_keys.py        # corpus-api-keys CLI
│   │   ├── manage_secrets.py     # corpus-secrets CLI
│   │   ├── rate_limiting.py
│   │   ├── secrets.py            # Keyring-backed secret storage
│   │   ├── security.py
│   │   └── validation.py
│   └── corpus_callosum/          # Additional modules (converters, storage, sync)
├── configs/                      # Configuration files
│   ├── base.yaml                 # Default configuration
│   └── examples/                 # Example configurations
├── tests/                        # Test suite
├── docs/                         # Documentation
└── .github/workflows/            # CI/CD
```

## Configuration

CorpusCallosum uses hierarchical YAML configuration:

1. **Base config** (`configs/base.yaml`) - shared settings
2. **Environment variables** - runtime overrides (e.g., `CC_LLM_MODEL=mistral`)
3. **CLI arguments** - highest precedence

### Example Configuration

```yaml
# configs/base.yaml
llm:
  endpoint: http://localhost:11434
  model: llama3
  timeout_seconds: 120.0
  temperature: 0.7

embedding:
  backend: ollama  # or sentence-transformers
  model: nomic-embed-text

database:
  backend: chromadb
  mode: persistent
  persist_directory: ./chroma_store

paths:
  vault: ./vault
  scratch_dir: ./scratch
  output_dir: ./output
```

## Architecture

### Design Principles

1. **Modularity**: Each tool works independently and can be used standalone
2. **Dual Access**: CLI interface + MCP server for agent orchestration
3. **Unified Database**: Single ChromaDB instance with namespaced collections
4. **Multi-LLM Support**: Pluggable backend system supporting multiple providers
5. **Configuration Hierarchy**: Flexible, overridable configuration system
6. **Secure by Default**: Keyring-backed secrets, API key authentication for MCP server

### LLM Backend Support

- **Ollama** (default): Local LLM inference with `/api/generate` endpoint
- **OpenAI-compatible**: Any API supporting `/v1/chat/completions`
- **Anthropic-compatible**: Claude API via `/v1/messages`

## Development

All developer workflows run through `corpus dev` — no shell scripts needed, identical on every platform:

```bash
corpus dev setup       # install in editable mode
corpus dev test        # run pytest
corpus dev test --cov  # run with coverage
corpus dev lint        # ruff check + mypy
corpus dev fmt         # ruff format
corpus dev build       # build wheel/sdist
corpus dev clean       # remove __pycache__ and build artifacts
```

Or use the underlying tools directly:

```bash
pip install -e ".[dev]"
pytest tests/
pytest --cov=src tests/
ruff check src/ tests/
mypy src/
ruff format src/ tests/
```

## Documentation

- **[Architecture Overview](docs/phases/)**: Detailed system design and implementation phases
- **[Tool Documentation](docs/tools-usage.md)**: Individual tool usage and examples
- **[MCP Integration](docs/mcp-integration.md)**: Agent orchestration setup
- **[Configuration Guide](docs/configuration.md)**: Advanced configuration examples
- **[Docker Setup](docs/docker.md)**: Container deployment
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run quality checks (`ruff check`, `mypy`, `pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [ChromaDB](https://www.trychroma.com/) for vector storage
- LLM integration via [Ollama](https://ollama.ai/) and compatible APIs
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) for agent integration
- Video transcription powered by [Whisper](https://openai.com/research/whisper)

---

**CorpusCallosum**: Bridging your knowledge, powered by AI.
