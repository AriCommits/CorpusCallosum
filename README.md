# CorpusCallosum

**Unified Learning & Knowledge Management Toolkit**

A modular, AI-powered system for personal knowledge management with RAG (Retrieval-Augmented Generation), flashcard generation, video transcription, and intelligent study workflows.

## ✨ Features

### 🎯 **Core Tools**
- **📚 RAG Agent**: Query your personal knowledge base with intelligent context-aware responses
- **🧠 Flashcard Generator**: Create study cards from your documents with AI-powered Q&A generation
- **📝 Summary Generator**: Generate comprehensive summaries with key insights and outlines
- **❓ Quiz Generator**: Build interactive quizzes with multiple choice, true/false, and short answer questions
- **🎥 Video Transcriber**: Convert lectures and videos to searchable text with AI-powered cleaning

### 🔧 **Advanced Features**
- **🤖 Multi-LLM Backend Support**: Ollama, OpenAI-compatible, and Anthropic-compatible APIs
- **🔌 MCP Server Integration**: All tools accessible via Model Context Protocol for agent orchestration
- **⚡ Dual Interface**: Every tool works standalone via CLI or through MCP for agent workflows
- **🗄️ Unified Database**: Single ChromaDB instance with intelligent collection management
- **📋 Pre-Built Orchestrations**: Study sessions, lecture processing pipelines, and knowledge base workflows

## 🚀 Quick Start

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

## 🛠️ Usage

### Individual Tools (CLI)

```bash
# RAG queries
corpus-rag ingest --path ./documents --collection notes
corpus-rag query --collection notes --query "What is machine learning?"

# Generate flashcards
corpus-flashcards --collection notes --count 15 --difficulty intermediate

# Create summaries
corpus-summaries --collection notes --topic "artificial intelligence"

# Build quizzes
corpus-quizzes --collection notes --difficulty advanced --count 10

# Transcribe videos
corpus-video transcribe --input lecture.mp4 --output transcript.txt --clean

# Run pre-composed workflows
corpus-orchestrate study-session --collection notes --topic "databases"
```

### MCP Server (Agent Integration)

Start the MCP server to expose all tools to AI agents:

```bash
# Start MCP server
corpus-mcp-server

# Server runs on http://localhost:8000/mcp
```

Configure your AI agent to connect to the MCP server and access tools like:
- `generate_flashcards(collection="notes", count=10)`
- `rag_query(collection="notes", query="Explain quantum computing")`
- `transcribe_video(video_path="lecture.mp4", clean=True)`

## 📁 Project Structure

```
CorpusCallosum/
├── src/corpus_callosum/          # Main package
│   ├── tools/                    # Individual tool implementations
│   │   ├── rag/                 # RAG agent (ingest, query, retrieval)
│   │   ├── flashcards/          # Flashcard generation
│   │   ├── summaries/           # Summary generation
│   │   ├── quizzes/             # Quiz generation
│   │   └── video/               # Video transcription & cleaning
│   ├── llm/                     # LLM backend abstraction
│   ├── db/                      # Database layer (ChromaDB)
│   ├── config/                  # Configuration management
│   ├── mcp_server/              # MCP server implementation
│   └── orchestrations/          # Pre-composed workflows
├── configs/                      # Configuration files
│   ├── base.yaml                # Default configuration
│   └── examples/                # Example configurations
├── tests/                       # Test suite
├── docs/                        # Documentation
└── .github/workflows/           # CI/CD
```

## 🔧 Configuration

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

## 🏗️ Architecture

### Design Principles

1. **Modularity**: Each tool works independently and can be used standalone
2. **Dual Access**: CLI interface + MCP server for agent orchestration
3. **Unified Database**: Single ChromaDB instance with namespaced collections
4. **Multi-LLM Support**: Pluggable backend system supporting multiple providers
5. **Configuration Hierarchy**: Flexible, overridable configuration system

### LLM Backend Support

- **Ollama** (default): Local LLM inference with `/api/generate` endpoint
- **OpenAI-compatible**: Any API supporting `/v1/chat/completions`
- **Anthropic-compatible**: Claude API via `/v1/messages`

## 🧪 Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=corpus_callosum tests/
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Auto-formatting
ruff format src/ tests/
```

## 📚 Documentation

- **[Architecture Overview](docs/phases/)**: Detailed system design and implementation phases
- **[Tool Documentation](src/corpus_callosum/tools/)**: Individual tool specifications
- **[MCP Integration](src/corpus_callosum/mcp_server/)**: Agent orchestration setup
- **[Configuration Guide](configs/examples/)**: Advanced configuration examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run quality checks (`ruff check`, `mypy`, `pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [ChromaDB](https://www.trychroma.com/) for vector storage
- LLM integration via [Ollama](https://ollama.ai/) and compatible APIs
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) for agent integration
- Video transcription powered by [Whisper](https://openai.com/research/whisper)

---

**CorpusCallosum**: Bridging your knowledge, powered by AI. 🧠✨