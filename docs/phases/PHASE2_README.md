# Phase 2 Implementation: Tool Migration

**Status**: ✅ Complete  
**Version**: 0.3.0  
**Timeline**: Weeks 3-4 of 8-week plan

## Overview

Phase 2 focused on migrating and restructuring existing tool capabilities into the new unified architecture. All five core tools have been successfully migrated with consistent patterns, CLI interfaces, and configuration systems.

## Completed Components

### 1. Tool Structure

All tools follow the consistent pattern defined in the architecture plan:

```
src/corpus_callosum/tools/
├── rag/                    # Retrieval-Augmented Generation
│   ├── __init__.py         # Exports: RAGConfig, RAGAgent, RAGRetriever, RAGIngester
│   ├── config.py           # ChunkingConfig, RetrievalConfig, RAGConfig
│   ├── retriever.py        # Semantic & hybrid search, RetrievedChunk model
│   ├── agent.py            # RAGAgent orchestration, prompt building
│   ├── ingest.py           # Document ingestion (.md, .txt, .pdf)
│   └── cli.py              # Click-based CLI: ingest, query, chat
├── flashcards/
│   ├── __init__.py
│   ├── config.py           # FlashcardConfig
│   ├── generator.py        # FlashcardGenerator (placeholder impl)
│   └── cli.py              # Generate flashcards from collections
├── summaries/
│   ├── __init__.py
│   ├── config.py           # SummaryConfig
│   ├── generator.py        # SummaryGenerator (placeholder impl)
│   └── cli.py              # Generate summaries from collections
├── quizzes/
│   ├── __init__.py
│   ├── config.py           # QuizConfig with question type & difficulty distribution
│   ├── generator.py        # QuizGenerator (placeholder impl)
│   └── cli.py              # Generate quizzes from collections
└── video/
    ├── __init__.py
    ├── config.py           # VideoConfig (Whisper + Ollama settings)
    ├── transcribe.py       # VideoTranscriber (faster-whisper integration)
    ├── clean.py            # TranscriptCleaner (Ollama-based cleanup)
    ├── augment.py          # TranscriptAugmenter (manual editing support)
    └── cli.py              # Complete video pipeline CLI
```

### 2. RAG Tool (Fully Migrated)

**Source**: `rag/src/` → `src/corpus_callosum/tools/rag/`

**Key Features**:
- **Retriever**: Semantic search using database backend, hybrid search placeholder for BM25 integration
- **Agent**: Query orchestration, prompt building with retrieved context
- **Ingester**: Document chunking and indexing (.md, .txt, .pdf support)
- **CLI**: Interactive chat, one-shot query, document ingestion

**Config Structure**:
```yaml
rag:
  chunking:
    chunk_size: 512
    overlap: 50
  retrieval:
    top_k: 5
  collection_prefix: "rag"
```

**CLI Examples**:
```bash
# Ingest documents
corpus-rag ingest ~/notes/physics -c physics101

# Query collection
corpus-rag query "What is quantum entanglement?" -c physics101

# Interactive chat
corpus-rag chat -c physics101
```

### 3. Flashcards Tool

**Features**:
- Configurable cards_per_topic, difficulty_levels
- Multiple output formats: anki, quizlet, plain
- Database integration for source material retrieval
- Placeholder LLM generation (to be implemented in Phase 4)

**Config Structure**:
```yaml
flashcards:
  cards_per_topic: 10
  difficulty_levels: ["basic", "intermediate", "advanced"]
  format: "anki"
  collection_prefix: "flashcards"
  max_context_chars: 12000
```

**CLI Example**:
```bash
corpus-flashcards -c biology -d advanced -n 20 -o flashcards.txt
```

### 4. Summaries Tool

**Features**:
- Configurable summary length (short/medium/long)
- Optional keywords and outline extraction
- Markdown output format
- Database-backed content retrieval

**Config Structure**:
```yaml
summaries:
  summary_length: "medium"
  include_keywords: true
  include_outline: true
  collection_prefix: "summaries"
  max_context_chars: 15000
```

**CLI Example**:
```bash
corpus-summaries -c biology -l long -o summary.md
```

### 5. Quizzes Tool

**Features**:
- Multiple question types: multiple_choice, true_false, short_answer
- Configurable difficulty distribution
- Output formats: markdown, json, csv
- Optional explanations for answers

**Config Structure**:
```yaml
quizzes:
  questions_per_topic: 15
  question_types: ["multiple_choice", "true_false", "short_answer"]
  difficulty_distribution:
    easy: 0.3
    medium: 0.5
    hard: 0.2
  format: "markdown"
  include_explanations: true
```

**CLI Example**:
```bash
corpus-quizzes -c biology -n 25 -fmt json -o quiz.json
```

### 6. Video Tool (Fully Migrated)

**Source**: `video_transcribe/` → `src/corpus_callosum/tools/video/`

**Features**:
- **Transcribe**: faster-whisper integration for video-to-text
- **Clean**: Ollama-based transcript cleanup (remove filler, preserve facts)
- **Augment**: Manual annotation support with editor integration
- **Pipeline**: Complete end-to-end workflow

**Config Structure**:
```yaml
video:
  whisper_model: "medium.en"
  whisper_device: "cuda"
  whisper_compute_type: "float16"
  whisper_language: "en"
  clean_model: "qwen3:8b"
  clean_ollama_host: "http://localhost:11434"
  output_format: "markdown"
  include_timestamps: false
```

**CLI Examples**:
```bash
# Transcribe only
corpus-video transcribe ~/videos/lecture1 -c BIOL101 -l 1

# Clean transcript
corpus-video clean raw_transcript.md -o cleaned.md

# Full pipeline
corpus-video pipeline ~/videos/lecture1 -c BIOL101 -l 1
```

### 7. Testing Infrastructure

**New Test File**: `tests/unit/test_tools.py`

**Coverage**:
- Import tests for all tools
- Config creation from dict for all tools
- Basic validation of config parameters

**Test Count**: 10 unit tests covering all 5 tools

### 8. Updated Dependencies

Added to `pyproject.toml`:
- `click>=8.1.0` - CLI framework
- `ollama>=0.4.0` - Ollama API client for transcript cleaning

Optional dependencies remain available:
- `faster-whisper` - Video transcription
- `pypdf` - PDF ingestion

## Architecture Highlights

### Consistent Config Pattern

Every tool extends `BaseConfig` and implements `from_dict()`:

```python
@dataclass
class FlashcardConfig(BaseConfig):
    cards_per_topic: int = 10
    format: str = "anki"
    
    @classmethod
    def from_dict(cls, data: dict) -> "FlashcardConfig":
        base_config = super().from_dict(data)
        flashcard_data = data.get("flashcards", {})
        return cls(
            llm=base_config.llm,
            database=base_config.database,
            paths=base_config.paths,
            cards_per_topic=flashcard_data.get("cards_per_topic", 10),
            ...
        )
```

### CLI Pattern

All CLIs use Click for consistency:

```python
@click.command()
@click.option('--collection', '-c', required=True)
@click.option('--config', '-f', default='configs/base.yaml')
def tool_command(collection: str, config: str):
    config_data = load_config(config)
    cfg = ToolConfig.from_dict(config_data)
    db = ChromaDBBackend(cfg.database)
    tool = ToolGenerator(cfg, db)
    ...
```

### Database Integration

All tools use the unified `DatabaseBackend` abstraction:

```python
# Initialize DB from config
db = ChromaDBBackend(config.database)

# Check collection exists
if not db.collection_exists(full_collection):
    raise ValueError(...)

# Query for context
results = db.query(collection_name, query_text, n_results=top_k)
```

## Migration Notes

### Deferred to Later Phases

1. **LLM Integration**: Flashcards, summaries, and quizzes use placeholder generators. Real LLM-based generation will be implemented in Phase 4.

2. **MCP Server**: Tool wrappers for MCP exposure deferred to Phase 3 per plan.

3. **Advanced RAG**: BM25 keyword search and Reciprocal Rank Fusion (RRF) have placeholders. Full hybrid retrieval pending.

4. **Conversation Memory**: RAG chat has session_id parameter but memory persistence not yet implemented.

### Breaking Changes from Legacy Code

- **Config paths**: Old tools used `pipeline/config.yml`, new system uses `configs/base.yaml`
- **Import paths**: `from rag.src.agent` → `from corpus_callosum.tools.rag`
- **CLI names**: `python transcribe.py` → `corpus-video transcribe`

## Verification

### Manual Verification Steps

1. **Import Check**:
```python
from corpus_callosum.tools.rag import RAGConfig, RAGAgent
from corpus_callosum.tools.flashcards import FlashcardGenerator
from corpus_callosum.tools.video import VideoTranscriber
```

2. **Config Loading**:
```python
from corpus_callosum.config.loader import load_config
config_data = load_config("configs/base.yaml")
rag_cfg = RAGConfig.from_dict(config_data)
```

3. **CLI Help**:
```bash
python -m corpus_callosum.tools.rag.cli --help
python -m corpus_callosum.tools.flashcards.cli --help
```

### Test Execution

Tests written in `tests/unit/test_tools.py`. Execution requires conda environment:

```bash
conda activate cc
pytest tests/unit/test_tools.py -v
```

## Next Steps (Phase 3)

As outlined in the architecture plan:

1. **MCP Server Implementation**
   - Create `src/corpus_callosum/mcp_server/`
   - Implement tool registry
   - Add MCP wrappers for each tool
   - Expose unified MCP endpoint

2. **CLI Entry Points**
   - Register `corpus-rag`, `corpus-flashcards`, etc. in `pyproject.toml`
   - Test standalone CLI execution
   - Add shell completion support

3. **Enhanced Testing**
   - Integration tests for each tool
   - End-to-end workflow tests
   - CLI integration tests

4. **Documentation**
   - User guide for each tool
   - MCP integration examples
   - Configuration reference

## Lessons Learned

1. **Placeholder Strategy**: Implementing placeholder generators allowed us to complete the structure without blocking on LLM integration.

2. **Config Inheritance**: The `BaseConfig` pattern worked well for sharing LLM, database, and paths config across all tools.

3. **Database Abstraction**: The `DatabaseBackend` interface successfully decoupled tools from ChromaDB specifics.

4. **Click Framework**: Using Click provided consistent CLI patterns with minimal boilerplate.

## Summary

Phase 2 successfully migrated all five core tools into the unified architecture:

✅ **RAG**: Full retrieval, agent, and ingestion pipeline  
✅ **Flashcards**: Config + generator structure ready for LLM  
✅ **Summaries**: Config + generator structure ready for LLM  
✅ **Quizzes**: Config + generator structure with multiple question types  
✅ **Video**: Complete transcription, cleaning, and augmentation pipeline  

All tools share:
- Unified config system (BaseConfig + YAML)
- Database abstraction (DatabaseBackend)
- Consistent CLI interface (Click)
- Import-ready package structure

**Version**: 0.3.0  
**Committed**: Phase 2 implementation  
**Next**: Phase 3 - MCP Server & Orchestrations
