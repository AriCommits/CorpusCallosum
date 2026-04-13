# CorpusCallosum Configuration Guide

This guide covers all aspects of configuring CorpusCallosum, from basic setup to advanced customization.

## Configuration System Overview

CorpusCallosum uses a hierarchical YAML-based configuration system that allows flexible customization while maintaining sensible defaults. The configuration system supports:

- **Hierarchical loading**: Base configuration + tool-specific overrides
- **Environment variables**: Runtime overrides using `CC_*` prefix
- **CLI arguments**: Highest precedence overrides
- **Deep merging**: Nested configuration sections merge intelligently
- **Type validation**: Configuration values are validated and type-checked

## Configuration Loading Order

Configuration values are loaded in the following order (later values override earlier ones):

1. **Base Configuration** (`configs/base.yaml`) - Shared defaults
2. **Tool-specific Configuration** (if applicable) - Tool overrides
3. **Environment Variables** (`CC_*` prefix) - Runtime overrides
4. **CLI Arguments** - Highest precedence

### Example Loading Process

```bash
# Base config has llm.model = "llama3"
# Tool config has llm.model = "llama3.2"
# Environment: CC_LLM_MODEL=mistral
# CLI: --model qwen3

# Final result: model = "qwen3" (CLI wins)
```

## Base Configuration

The base configuration file (`configs/base.yaml`) contains shared settings inherited by all tools.

### Complete Base Configuration

```yaml
# CorpusCallosum Base Configuration
# This file contains shared settings inherited by all tools

llm:
  endpoint: http://localhost:11434
  model: llama3
  backend: ollama                    # ollama | openai_compatible | anthropic_compatible
  timeout_seconds: 120.0
  temperature: 0.7
  max_tokens: null                   # null for model default
  api_key: null                      # For cloud providers
  fallback_models: []                # Fallback model list

embedding:
  backend: ollama                    # ollama | sentence-transformers
  model: nomic-embed-text
  dimensions: null                   # Auto-detect if null

database:
  backend: chromadb
  mode: persistent                   # persistent | http
  host: localhost                    # For HTTP mode
  port: 8000
  persist_directory: ./chroma_store

paths:
  vault: ./vault                     # Document storage
  scratch_dir: ./scratch             # Temporary files
  output_dir: ./output               # Generated content
```

## Configuration Sections

### LLM Configuration

Controls how CorpusCallosum connects to Large Language Models.

```yaml
llm:
  endpoint: http://localhost:11434   # LLM service endpoint
  model: llama3                      # Primary model name
  backend: ollama                    # Backend type
  timeout_seconds: 120.0             # Request timeout
  temperature: 0.7                   # Sampling temperature (0.0-1.0)
  max_tokens: null                   # Max response tokens (null=model default)
  api_key: null                      # API key for cloud providers
  fallback_models:                   # Fallback models if primary fails
    - llama3.1
    - qwen2
```

#### Supported Backends

**Ollama Backend** (`backend: ollama`):
```yaml
llm:
  backend: ollama
  endpoint: http://localhost:11434
  model: llama3
  # No API key required
```

**OpenAI Compatible** (`backend: openai_compatible`):
```yaml
llm:
  backend: openai_compatible
  endpoint: https://api.openai.com/v1
  model: gpt-4
  api_key: sk-your-api-key-here
```

**Anthropic Compatible** (`backend: anthropic_compatible`):
```yaml
llm:
  backend: anthropic_compatible
  endpoint: https://api.anthropic.com
  model: claude-3-sonnet-20240229
  api_key: your-anthropic-api-key
```

### Embedding Configuration

Controls document embedding generation for vector search.

```yaml
embedding:
  backend: ollama                    # ollama | sentence-transformers
  model: nomic-embed-text           # Embedding model name
  dimensions: null                   # Vector dimensions (auto-detect if null)
```

#### Ollama Embeddings

```yaml
embedding:
  backend: ollama
  model: nomic-embed-text           # Or: all-minilm, bge-large, etc.
  dimensions: null                   # Auto-detected from model
```

#### Sentence-Transformers Embeddings

```yaml
embedding:
  backend: sentence-transformers
  model: all-MiniLM-L6-v2          # HuggingFace model name
  dimensions: 384                   # Model-specific dimensions
```

### Database Configuration

Controls ChromaDB vector database connection.

```yaml
database:
  backend: chromadb
  mode: persistent                   # persistent | http
  host: localhost                    # For HTTP mode
  port: 8000                        # For HTTP mode
  persist_directory: ./chroma_store  # For persistent mode
```

#### Persistent Mode (Local Files)

```yaml
database:
  backend: chromadb
  mode: persistent
  persist_directory: ./chroma_store
```

Best for:
- Single-user setups
- Development
- Local testing
- Offline usage

#### HTTP Mode (Client-Server)

```yaml
database:
  backend: chromadb
  mode: http
  host: localhost                    # ChromaDB server host
  port: 8000                        # ChromaDB server port
```

Best for:
- Multi-user environments
- Docker deployments
- Shared databases
- Production setups

### Paths Configuration

Controls file system locations for various data.

```yaml
paths:
  vault: ./vault                     # Document storage directory
  scratch_dir: ./scratch             # Temporary files
  output_dir: ./output               # Generated content output
```

#### Custom Path Examples

```yaml
paths:
  vault: ~/Documents/corpus-vault
  scratch_dir: ~/.cache/corpus-callosum
  output_dir: ~/Documents/corpus-output
```

## Tool-Specific Configuration

Individual tools can extend the base configuration with tool-specific settings.

### RAG Configuration

```yaml
# Inherit from base configuration, then add:
rag:
  chunking:
    size: 500                        # Chunk size in characters
    overlap: 50                      # Overlap between chunks
  retrieval:
    top_k_semantic: 10               # Semantic search results
    top_k_bm25: 10                   # Keyword search results
    top_k_final: 5                   # Final combined results
    rrf_k: 60                        # Reciprocal Rank Fusion parameter
  collection_prefix: "rag"           # Collection name prefix
```

### Flashcards Configuration

```yaml
flashcards:
  cards_per_topic: 15                # Default cards to generate
  difficulty_levels:                 # Available difficulty levels
    - basic
    - intermediate
    - advanced
  format: anki                       # Output format: anki | quizlet | plain
  collection_prefix: "flashcards"    # Collection name prefix
  max_context_chars: 12000           # Max context for generation
```

### Summaries Configuration

```yaml
summaries:
  default_length: medium             # short | medium | long | custom
  include_keywords: true             # Include keyword extraction
  max_context_chars: 15000           # Max context for generation
  collection_prefix: "summaries"     # Collection name prefix
```

### Quizzes Configuration

```yaml
quizzes:
  question_types:                    # Available question types
    - multiple_choice
    - true_false
    - short_answer
    - essay
  default_count: 10                  # Default questions to generate
  format: plain                      # Output format
  collection_prefix: "quizzes"       # Collection name prefix
  max_context_chars: 12000           # Max context for generation
```

### Video Configuration

```yaml
video:
  transcription:
    model: base                      # Whisper model: tiny | base | small | medium | large
    language: auto                   # Language code or 'auto'
  processing:
    chunk_size: 30                   # Seconds per chunk for processing
  collection_prefix: "video"         # Collection name prefix
```

## Environment Variable Overrides

Any configuration value can be overridden using environment variables with the `CC_` prefix.

### Environment Variable Format

Convert YAML paths to environment variables:
- Nested keys: `llm.model` → `CC_LLM_MODEL`
- Array indices: Not directly supported
- Underscores: Use for nested access

### Common Environment Variables

```bash
# LLM Configuration
export CC_LLM_ENDPOINT=http://localhost:11434
export CC_LLM_MODEL=llama3
export CC_LLM_BACKEND=ollama
export CC_LLM_TEMPERATURE=0.7
export CC_LLM_API_KEY=your-api-key

# Database Configuration
export CC_DATABASE_MODE=http
export CC_DATABASE_HOST=chromadb
export CC_DATABASE_PORT=8001

# Paths Configuration
export CC_PATHS_VAULT=/path/to/documents
export CC_PATHS_OUTPUT_DIR=/path/to/output

# Tool-specific Configuration
export CC_RAG_CHUNKING_SIZE=1000
export CC_FLASHCARDS_CARDS_PER_TOPIC=20
```

### Docker Environment Variables

For Docker deployments, you can set environment variables in your compose file:

```yaml
services:
  corpus-mcp:
    image: corpus-callosum:latest
    environment:
      - CC_DATABASE_MODE=http
      - CC_DATABASE_HOST=chromadb
      - CC_DATABASE_PORT=8000
      - CC_LLM_ENDPOINT=http://ollama:11434
      - CC_LLM_MODEL=llama3
```

## Configuration Examples

### Example 1: Minimal Local Setup

```yaml
# configs/minimal.yaml
llm:
  endpoint: http://localhost:11434
  model: llama3

database:
  mode: persistent
  persist_directory: ./chroma_store
```

### Example 2: Production Docker Setup

```yaml
# configs/production.yaml
llm:
  endpoint: http://ollama:11434
  model: llama3
  timeout_seconds: 180.0

database:
  mode: http
  host: chromadb
  port: 8000

paths:
  vault: /app/data/vault
  scratch_dir: /tmp/corpus-scratch
  output_dir: /app/data/output
```

### Example 3: Cloud LLM Setup

```yaml
# configs/cloud.yaml
llm:
  backend: openai_compatible
  endpoint: https://api.openai.com/v1
  model: gpt-4
  api_key: ${OPENAI_API_KEY}  # Use environment variable
  temperature: 0.3
  max_tokens: 4000

embedding:
  backend: sentence-transformers
  model: all-MiniLM-L6-v2
  dimensions: 384

database:
  mode: http
  host: your-chromadb-server.com
  port: 8000
```

### Example 4: Advanced RAG Configuration

```yaml
# configs/advanced-rag.yaml
llm:
  endpoint: http://localhost:11434
  model: llama3
  fallback_models:
    - llama3.1
    - qwen2

embedding:
  backend: ollama
  model: nomic-embed-text

database:
  mode: persistent
  persist_directory: ./advanced_chroma

rag:
  chunking:
    size: 1000
    overlap: 100
  retrieval:
    top_k_semantic: 15
    top_k_bm25: 15
    top_k_final: 8
    rrf_k: 60

paths:
  vault: ~/Documents/research-papers
  output_dir: ~/Documents/rag-outputs
```

## Configuration Validation

CorpusCallosum validates configuration at startup and provides clear error messages for invalid settings.

### Common Validation Errors

**Missing Required Fields**:
```
Error: Missing required field 'llm.model' in configuration
```

**Invalid Backend**:
```
Error: Invalid LLM backend 'invalid_backend'. Must be one of: ollama, openai_compatible, anthropic_compatible
```

**Invalid Path**:
```
Error: Database persist_directory '/invalid/path' does not exist and cannot be created
```

**Type Mismatch**:
```
Error: Field 'llm.temperature' must be a float, got string
```

## Configuration Best Practices

### 1. Use Base Configuration

Always start with a base configuration and override only what you need:

```yaml
# Good: Minimal overrides
llm:
  model: llama3.1  # Only override what's different

# Avoid: Repeating entire configuration
```

### 2. Environment-Specific Configs

Use separate configuration files for different environments:

```
configs/
├── base.yaml        # Shared defaults
├── development.yaml # Local development
├── production.yaml  # Production deployment
└── testing.yaml     # Test environment
```

### 3. Secure API Keys

Never commit API keys to version control. Use environment variables:

```yaml
llm:
  api_key: null  # Set via CC_LLM_API_KEY environment variable
```

### 4. Use Absolute Paths in Production

For production deployments, use absolute paths:

```yaml
paths:
  vault: /app/data/vault
  output_dir: /app/data/output
  persist_directory: /app/data/chroma
```

### 5. Resource Limits

Consider resource limits for production:

```yaml
llm:
  timeout_seconds: 300.0  # Longer timeout for production
  max_tokens: 4000        # Reasonable limit

rag:
  chunking:
    size: 1000            # Larger chunks for better context
  retrieval:
    top_k_final: 10       # More results for better recall
```

### 6. Monitoring and Logging

In production, consider adding observability configuration:

```yaml
# Additional configuration for monitoring
observability:
  telemetry_endpoint: http://jaeger:14268/api/traces
  metrics_enabled: true
  log_level: info
```

## Troubleshooting Configuration

### Check Current Configuration

Use the configuration inspection commands:

```bash
# Check effective configuration
corpus-config show

# Validate configuration
corpus-config validate

# Show configuration sources
corpus-config sources
```

### Common Issues

**Database Connection Failed**:
- Check `database.mode` and connection details
- Verify ChromaDB server is running (for HTTP mode)
- Check file permissions (for persistent mode)

**LLM Connection Failed**:
- Verify `llm.endpoint` is correct and accessible
- Check if API key is set (for cloud providers)
- Confirm model is available

**Path Issues**:
- Ensure directories exist and are writable
- Use absolute paths for production
- Check file permissions

**Environment Variable Not Applied**:
- Verify variable name format (`CC_SECTION_FIELD`)
- Check variable is exported in shell
- Confirm no typos in variable names

## Advanced Configuration

### Custom Configuration Classes

For advanced use cases, you can extend the configuration system:

```python
from corpus_callosum.config.base import BaseConfig
from dataclasses import dataclass, field

@dataclass
class MyCustomConfig(BaseConfig):
    """Custom configuration for specialized tool."""
    
    custom_setting: str = "default_value"
    advanced_options: dict = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> "MyCustomConfig":
        # Custom loading logic
        base_config = super().from_dict(data)
        return cls(
            llm=base_config.llm,
            database=base_config.database,
            # ... other fields
            custom_setting=data.get("custom_setting", "default_value")
        )
```

### Configuration Hooks

You can add configuration validation hooks:

```python
def validate_config(config: BaseConfig) -> None:
    """Custom configuration validation."""
    if config.llm.temperature > 1.0:
        raise ValueError("Temperature must be <= 1.0")
    
    if not config.paths.vault.exists():
        config.paths.vault.mkdir(parents=True, exist_ok=True)
```

This configuration system provides flexible, powerful configuration management while maintaining simplicity for common use cases.