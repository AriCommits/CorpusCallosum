# CorpusCallosum Architecture Overview

CorpusCallosum is a modular, AI-powered learning and knowledge management toolkit designed around the principle of **dual access patterns**. The system provides both standalone CLI tools and a unified MCP (Model Context Protocol) server for AI agent orchestration.

## System Architecture

### Core Design Principles

1. **Layered Architecture**: Clear separation between configuration, database, LLM backend, tools, and orchestrations
2. **Plugin-Based Design**: Extensible tool system with consistent interfaces
3. **Dual Access Pattern**: Every tool accessible via both CLI and MCP server
4. **Unified Data Layer**: Single ChromaDB instance with namespaced collections
5. **Configuration Hierarchy**: Flexible, overridable YAML-based configuration system
6. **Multi-LLM Backend Support**: Pluggable backend system for different LLM providers

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CorpusCallosum System                        │
├─────────────────────────────────────────────────────────────────┤
│  Access Layer                                                   │
│  ┌─────────────────┐           ┌─────────────────────────────┐   │
│  │   CLI Tools     │           │      MCP Server             │   │
│  │   Individual    │           │   (Agent Integration)       │   │
│  │   Commands      │           │   FastAPI + FastMCP        │   │
│  └─────────────────┘           └─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Orchestration Layer                                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Pre-Built Workflows (Study Session, Lecture Pipeline)     │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Tools Layer                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │   RAG    │ │Flashcards│ │Summaries │ │ Quizzes  │ │ Video  │ │
│  │  Agent   │ │Generator │ │Generator │ │Generator │ │Process │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Backend Services Layer                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────────┐  │
│  │     LLM      │ │  Database    │ │     Configuration      │  │
│  │   Backend    │ │  Abstraction │ │      Management        │  │
│  │  (Multi)     │ │  (ChromaDB)  │ │   (Hierarchical)       │  │
│  └──────────────┘ └──────────────┘ └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Modules

### Configuration System (`config/`)

**Purpose**: Hierarchical YAML-based configuration with environment variable overrides

**Key Components**:
- `base.py`: Configuration dataclasses (`BaseConfig`, `LLMConfig`, `DatabaseConfig`, etc.)
- `loader.py`: Configuration loading with deep merge support
- `schema.py`: Validation schemas for configuration integrity

**Hierarchical Loading Order**:
1. Base Configuration (`configs/base.yaml`)
2. Tool-specific Configuration (if applicable)
3. Environment Variables (`CC_*` prefix)
4. CLI Arguments (highest precedence)

**Configuration Structure**:
```yaml
llm:
  endpoint: http://localhost:11434
  model: llama3
  backend: ollama                    # ollama | openai_compatible | anthropic_compatible
  temperature: 0.7

database:
  backend: chromadb
  mode: persistent                   # persistent | http
  persist_directory: ./chroma_store

paths:
  vault: ./vault                     # Document storage
  output_dir: ./output               # Generated content

# Tool-specific configurations
flashcards:
  cards_per_topic: 15
  format: anki

rag:
  chunking:
    size: 500
    overlap: 50
  retrieval:
    top_k_final: 5
```

### Database Abstraction Layer (`db/`)

**Purpose**: Unified vector database interface with ChromaDB implementation

**Key Components**:
- `base.py`: Abstract `DatabaseBackend` interface
- `chroma.py`: ChromaDB implementation with persistent/HTTP modes
- `models.py`: Data models (`Document`, `Collection`, `QueryResult`)
- `management.py`: CLI for database operations (`corpus-db`)

**Architecture Features**:
- **Abstract backend interface**: Pluggable database implementations
- **Collection-based organization**: Namespaced document storage
- **Dual connection modes**: Persistent file storage or HTTP client
- **Type-safe operations**: Structured data models for all operations

**Collection Namespace Strategy**:
| Tool | Collection Pattern | Example |
|------|-------------------|---------|
| Flashcards | `flashcards_<topic>` | `flashcards_biology` |
| Summaries | `summaries_<topic>` | `summaries_history` |
| RAG | `rag_<name>` | `rag_lecture_notes` |
| Video | `video_<course>` | `video_cs101` |

### LLM Backend System (`llm/`)

**Purpose**: Multi-provider LLM abstraction with streaming support

**Key Components**:
- `backend.py`: Abstract base class and provider implementations
  - `OllamaBackend`: Local Ollama inference with auto-detection
  - `OpenAICompatibleBackend`: OpenAI-compatible APIs
  - `AnthropicCompatibleBackend`: Claude API support
- `config.py`: LLM configuration with backend selection
- `prompts.py`: Standardized prompt templates
- `response.py`: Response data structures

**Design Patterns**:
- **Strategy pattern**: Pluggable backend implementations
- **Factory pattern**: `create_backend()` for provider selection
- **Streaming support**: Iterator-based token streaming
- **Auto-detection**: Ollama model discovery
- **Fallback mechanisms**: Multiple model support per backend

### Tools Layer (`tools/`)

**Purpose**: Individual content generation and processing tools

Each tool follows a consistent structure:
```
tools/<tool_name>/
├── __init__.py       # Public API exports
├── config.py         # Tool-specific configuration (extends BaseConfig)
├── cli.py            # CLI interface
├── generator.py      # Core tool implementation
└── <specialized>.py  # Tool-specific modules
```

**Available Tools**:
- **RAG Tool** (`rag/`): Document ingestion, hybrid retrieval, and query orchestration
- **Flashcards** (`flashcards/`): Spaced repetition card generation
- **Summaries** (`summaries/`): Document summarization with keywords
- **Quizzes** (`quizzes/`): Multi-format question generation
- **Video** (`video/`): Transcription, cleaning, and augmentation

**Common Patterns**:
- Configuration inheritance from `BaseConfig`
- Database integration via `DatabaseBackend`
- LLM integration using shared backend system
- CLI standardization with Click framework

### MCP Server (`mcp_server/`)

**Purpose**: Model Context Protocol server for AI agent integration

**Key Components**:
- `server.py`: FastMCP server with tool registration
- Health endpoints (`/health`, `/health/ready`) for container orchestration
- Auto-generated tool discovery from individual tools

**Integration Pattern**:
- **Automatic tool exposure**: All CLI tools automatically available via MCP
- **Unified configuration**: Single config file for all tools
- **Resource management**: Collections and database state exposed as MCP resources
- **Prompt templates**: Pre-built prompts for common workflows

### Orchestrations (`orchestrations/`)

**Purpose**: Pre-composed workflows combining multiple tools

**Key Workflows**:
- `study_session.py`: Summary + Flashcards + Quiz generation
- `lecture_pipeline.py`: Video → Transcript → Clean → Ingest → Study Materials
- `knowledge_base.py`: Document ingestion and query workflows

**Design Pattern**:
- **Composition over inheritance**: Orchestrators compose multiple tools
- **Workflow templates**: Standardized multi-step processes
- **Result aggregation**: Combine outputs into comprehensive formats

## Access Patterns

### CLI Access Pattern

**Direct tool invocation** for individual tasks:

```bash
# Individual tool usage
corpus-rag ingest --path ./documents --collection notes
corpus-flashcards --collection notes --count 15
corpus-summaries --collection notes --topic "databases"

# Database management
corpus-db backup --collection notes --output notes-backup.tar.gz
corpus-db export --collection notes --format json

# Orchestrated workflows  
corpus-orchestrate study-session --collection notes --topic "SQL"
corpus-orchestrate lecture-pipeline video.mp4 --course CS101
```

**Characteristics**:
- **Stateless**: Each command is independent
- **File-based I/O**: Input/output through files and stdout
- **Configuration per invocation**: Config loaded for each command
- **Process isolation**: Separate process for each tool

### MCP Access Pattern

**Agent-driven orchestration** through protocol calls:

```python
# Agent can call tools programmatically
await client.call_tool("rag_ingest", {
    "path": "./documents", 
    "collection": "notes"
})

flashcards = await client.call_tool("generate_flashcards", {
    "collection": "notes",
    "count": 15,
    "difficulty": "intermediate"
})

# Multi-step workflows with state
summary = await client.call_tool("generate_summary", {"collection": "notes"})
quiz = await client.call_tool("generate_quiz", {"collection": "notes"})
```

**Available MCP Tools**:
- `rag_ingest()`, `rag_query()`, `rag_retrieve()`
- `generate_flashcards()`, `generate_summary()`, `generate_quiz()`
- `transcribe_video()`, `clean_transcript()`

**MCP Resources**:
- `collections://list`: List all collections
- `collection://{name}`: Get collection information

**MCP Prompts**:
- `study_session_prompt()`: Comprehensive study workflow
- `lecture_processing_prompt()`: Lecture processing workflow

**Characteristics**:
- **Stateful**: Shared database and configuration across calls
- **Programmatic**: JSON-based request/response
- **Session-based**: Persistent server process
- **Composition-friendly**: Easy to chain tool calls

### Dual Access Benefits

1. **Flexibility**: Users can choose interaction model
2. **Testability**: CLI commands are easily scriptable
3. **Agent Integration**: MCP enables AI-driven workflows
4. **Development**: CLI useful for debugging individual tools

## Docker Deployment Architecture

### Multi-Stage Build Strategy

The Docker architecture uses a multi-stage build for optimal deployment:

1. **Base Stage**: Python environment with system dependencies
2. **Development Stage**: Development dependencies + source mounting
3. **Production Stage**: Optimized for size and security
4. **CLI Stage**: Interactive container for CLI usage

### Container Orchestration

```yaml
services:
  # Vector Database
  chromadb:
    image: chromadb/chroma:0.4.24
    ports: ["8001:8000"]
    volumes: ["chroma-data:/chroma/chroma"]
    
  # LLM Service (Optional)
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama-data:/root/.ollama"]
    profiles: ["full", "ollama"]
    
  # Main Application
  corpus-mcp:
    build:
      context: .
      target: production
    depends_on: ["chromadb"]
    ports: ["8000:8000"]
    environment:
      - CC_DATABASE_HOST=chromadb
      - CC_LLM_ENDPOINT=http://ollama:11434
```

### Deployment Profiles

- **Minimal**: ChromaDB + MCP Server only
- **CLI**: Interactive container for command-line usage
- **Full**: All services including Ollama and observability
- **Development**: Hot reload with source mounting
- **Observability**: Includes Jaeger, OTEL collector

### Health Check Strategy

The system includes comprehensive health checks:
- MCP server responsiveness
- Database connectivity
- File system access
- Configuration validation

## Tool Integration Patterns

### Consistent Tool Structure

Every tool follows this standardized structure:

```python
class ToolGenerator:
    def __init__(self, config: ToolConfig, db: DatabaseBackend):
        self.config = config
        self.db = db
        self.llm_backend = create_backend(config.llm.to_backend_config())
    
    def generate(self, collection: str, **kwargs) -> str:
        # 1. Retrieve relevant documents from collection
        # 2. Build context-aware prompt
        # 3. Generate content using LLM
        # 4. Format and return result
```

### Common Integration Patterns

1. **Database Integration**: All tools receive `DatabaseBackend` instance
2. **LLM Integration**: Shared `LLMBackend` abstraction
3. **Configuration Integration**: Tool-specific config extends `BaseConfig`
4. **CLI Integration**: Click-based command interfaces
5. **MCP Integration**: Automatic tool discovery and registration

### RAG Tool Architecture

The RAG tool demonstrates advanced integration patterns:

```
RAG Tool
├── Ingester (Document Processing)
│   ├── File type detection
│   ├── Text extraction
│   ├── Chunking strategy
│   └── Embedding generation
├── Retriever (Hybrid Search)
│   ├── Semantic search (vector)
│   ├── Keyword search (BM25)
│   └── Reciprocal Rank Fusion
└── Agent (Response Generation)
    ├── Context assembly
    ├── Prompt templating
    └── LLM generation
```

## Error Handling and Resilience

1. **Configuration Validation**: Schema-based validation with clear error messages
2. **Database Error Handling**: Graceful handling of connection issues
3. **LLM Fallbacks**: Multiple model support with automatic fallback
4. **Resource Management**: Proper cleanup of temporary files and connections
5. **Health Monitoring**: Container health checks and observability integration

## Technology Stack

### Core Dependencies
- **FastAPI**: REST API framework for MCP server
- **ChromaDB**: Vector database for document storage
- **Click**: CLI framework for tool interfaces
- **Sentence-Transformers**: Embedding models (or Ollama)
- **PyYAML**: Configuration management
- **HTTPx**: HTTP client for LLM calls

### Optional Dependencies
- **OpenTelemetry**: Observability and tracing (via `[observability]` extra)
- **Faster-Whisper**: Video transcription
- **FFmpeg-Python**: Video processing

### Development Tools
- **pytest + pytest-cov**: Testing framework
- **ruff**: Code linting
- **mypy**: Static type checking

This architecture provides a solid foundation for building comprehensive learning and knowledge management workflows while maintaining flexibility, extensibility, and robustness across different deployment scenarios.