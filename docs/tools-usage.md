# CorpusCallosum Tool Usage Guide

This guide provides comprehensive documentation for all CorpusCallosum CLI tools, including usage patterns, options, and practical examples.

## Overview

CorpusCallosum provides 8 primary CLI commands that expose all functionality through consistent interfaces:

1. **`corpus-rag`** - RAG operations (ingest, query, chat)
2. **`corpus-flashcards`** - Generate study flashcards
3. **`corpus-summaries`** - Generate summaries 
4. **`corpus-quizzes`** - Generate quiz questions
5. **`corpus-video`** - Video transcription and processing
6. **`corpus-orchestrate`** - Pre-composed workflows
7. **`corpus-db`** - Database management operations
8. **`corpus-mcp-server`** - MCP server for agent integration

---

## 1. corpus-rag - RAG Operations

**Purpose**: Retrieval-Augmented Generation for document ingestion, querying, and interactive chat.

### Commands

#### `corpus-rag ingest`
Ingest documents into a RAG collection.

**Usage:**
```bash
corpus-rag ingest <PATH> --collection <NAME> [OPTIONS]
```

**Arguments:**
- `PATH` - Path to file or directory to ingest (required, must exist)

**Options:**
- `--collection, -c` - Collection name (required)
- `--config, -f` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Ingest documents from a directory
corpus-rag ingest ./documents --collection notes

# Ingest with custom config
corpus-rag ingest ./papers --collection research -f my-config.yaml

# Ingest single file
corpus-rag ingest document.pdf --collection personal
```

**Supported File Formats:**
- PDF (`.pdf`)
- Text files (`.txt`, `.md`)
- Word documents (`.docx`)
- HTML files (`.html`, `.htm`)
- RTF files (`.rtf`)

**Document Processing:**
- Automatic text extraction
- Intelligent chunking with overlap
- Embedding generation
- Metadata preservation

#### `corpus-rag query`
Query a RAG collection with a single question.

**Usage:**
```bash
corpus-rag query <QUERY> --collection <NAME> [OPTIONS]
```

**Arguments:**
- `QUERY` - Query string to search for (required)

**Options:**
- `--collection, -c` - Collection name (required)
- `--top-k, -k` - Number of results to retrieve (optional, default from config)
- `--config, -f` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Basic query
corpus-rag query "What is machine learning?" --collection notes

# Query with specific retrieval count
corpus-rag query "Explain neural networks" --collection ai -k 10

# Query with custom config
corpus-rag query "Database normalization" --collection cs -f production.yaml
```

**Query Features:**
- Hybrid search (semantic + keyword)
- Reciprocal rank fusion for result ranking
- Context-aware response generation
- Source attribution

#### `corpus-rag chat`
Interactive chat session with RAG agent.

**Usage:**
```bash
corpus-rag chat --collection <NAME> [OPTIONS]
```

**Options:**
- `--collection, -c` - Collection name (required)
- `--config, -f` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Start chat session
corpus-rag chat --collection notes

# Chat with custom config
corpus-rag chat --collection research -f research-config.yaml
```

**Interactive Commands:**
- Type your questions normally
- Type `exit` or `quit` to end session
- Use `Ctrl+C` or `Ctrl+D` to interrupt

**Chat Features:**
- Persistent conversation context
- Source document references
- Multi-turn conversations
- Real-time retrieval

---

## 2. corpus-flashcards - Flashcard Generation

**Purpose**: Generate AI-powered flashcards from document collections using spaced repetition principles.

### Usage
```bash
corpus-flashcards --collection <NAME> [OPTIONS]
```

### Options

- `--collection, -c` - Collection name (required)
- `--output, -o` - Output file path (optional, prints to stdout if not specified)
- `--config, -f` - Config file path (default: `configs/base.yaml`)
- `--difficulty, -d` - Difficulty level (default: `intermediate`)
- `--count, -n` - Number of flashcards to generate (optional, uses config default)

### Supported Difficulty Levels
- `basic` - Simple recall questions and definitions
- `intermediate` - Moderate complexity with examples
- `advanced` - Complex analysis and application questions

### Output Formats
Controlled via config file:
- `anki` - Anki import format with proper field separation
- `quizlet` - Quizlet import format
- `plain` - Simple text format for manual review

### Examples

```bash
# Generate 15 intermediate flashcards
corpus-flashcards --collection biology --count 15 --difficulty intermediate

# Output to file
corpus-flashcards --collection chemistry -o flashcards.txt --count 25

# Advanced difficulty cards
corpus-flashcards --collection physics --difficulty advanced --count 10

# Use custom config
corpus-flashcards --collection history -f custom.yaml
```

### Features
- **Context-aware generation**: Uses document context for relevant questions
- **Difficulty scaling**: Adjusts complexity based on difficulty level
- **Format flexibility**: Multiple output formats for different platforms
- **Deduplication**: Avoids generating duplicate or similar cards
- **Source tracking**: Maintains links to source documents

### Sample Output (Anki Format)
```
What is photosynthesis?	The process by which plants convert light energy into chemical energy using chlorophyll
Define enzyme specificity	The characteristic of enzymes to catalyze only specific reactions due to their unique active site shape
```

---

## 3. corpus-summaries - Summary Generation

**Purpose**: Generate comprehensive summaries from document collections with keyword extraction and structured output.

### Usage
```bash
corpus-summaries --collection <NAME> [OPTIONS]
```

### Options

- `--collection, -c` - Collection name (required)
- `--output, -o` - Output file path (optional, prints to stdout if not specified)
- `--config, -f` - Config file path (default: `configs/base.yaml`)
- `--length, -l` - Summary length (choices: `short`, `medium`, `long`, default: `medium`)

### Summary Lengths
- `short` - Brief overview with key points (300-500 words)
- `medium` - Balanced summary with details (800-1200 words)
- `long` - Comprehensive analysis with examples (1500+ words)

### Features
- **Keyword extraction**: Automatically identifies and highlights key terms
- **Structured output**: Organized with headers and sections
- **Context synthesis**: Combines information from multiple documents
- **Outline generation**: Creates logical information hierarchy

### Examples

```bash
# Generate medium-length summary
corpus-summaries --collection notes --length medium

# Short summary to file
corpus-summaries --collection lectures -l short -o summary.md

# Long detailed summary
corpus-summaries --collection research --length long

# Custom config
corpus-summaries --collection textbook -f detailed.yaml
```

### Sample Output Structure
```markdown
# Summary: Biology Collection

## Key Concepts
- Photosynthesis
- Cellular respiration
- DNA replication

## Overview
[Main summary content...]

## Important Points
1. [Key point 1]
2. [Key point 2]
3. [Key point 3]

## Keywords
- ATP, chloroplast, mitochondria, enzyme, protein synthesis
```

---

## 4. corpus-quizzes - Quiz Generation

**Purpose**: Generate interactive quizzes with multiple question types and comprehensive answer keys.

### Usage
```bash
corpus-quizzes --collection <NAME> [OPTIONS]
```

### Options

- `--collection, -c` - Collection name (required)
- `--output, -o` - Output file path (optional, prints to stdout if not specified)
- `--config, -f` - Config file path (default: `configs/base.yaml`)
- `--count, -n` - Number of questions (optional, uses config default)
- `--format, -fmt` - Output format (choices: `markdown`, `json`, `csv`, default: `markdown`)

### Question Types
Controlled via config:
- `multiple_choice` - Multiple choice questions with 4 options
- `true_false` - True/false questions with explanations
- `short_answer` - Short answer questions

### Output Formats
- `markdown` - Formatted markdown with questions and answers
- `json` - Structured JSON for programmatic use
- `csv` - Spreadsheet-compatible format for analysis

### Examples

```bash
# Generate 10 questions in markdown
corpus-quizzes --collection biology --count 10 --format markdown

# Export as JSON
corpus-quizzes --collection chemistry -n 15 --format json -o quiz.json

# CSV format for spreadsheet
corpus-quizzes --collection physics --format csv --count 20

# Custom config
corpus-quizzes --collection history -f quiz-config.yaml
```

### Features
- **Mixed question types**: Combines multiple choice, true/false, and short answer
- **Difficulty distribution**: Balanced mix of easy, medium, and hard questions
- **Answer explanations**: Detailed explanations for correct answers
- **Source references**: Links back to source documents
- **Randomization**: Shuffled options and question order

### Sample Output (Markdown)
```markdown
# Quiz: Biology Collection

## Question 1 (Multiple Choice)
What is the primary function of chlorophyll in photosynthesis?

A) To absorb carbon dioxide
B) To capture light energy
C) To produce oxygen
D) To create glucose

**Answer: B) To capture light energy**
**Explanation**: Chlorophyll is the primary pigment that absorbs light energy...

## Question 2 (True/False)
All enzymes are proteins.

**Answer: True**
**Explanation**: Enzymes are biological catalysts that are primarily proteins...
```

---

## 5. corpus-video - Video Processing Pipeline

**Purpose**: Comprehensive video transcription and processing toolkit using Whisper AI and LLM enhancement.

### Commands

#### `corpus-video transcribe`
Transcribe video files to text using Whisper.

**Usage:**
```bash
corpus-video transcribe <INPUT_FOLDER> [OPTIONS]
```

**Arguments:**
- `INPUT_FOLDER` - Path to folder containing video files (required, must exist)

**Options:**
- `--output, -o` - Output file path (optional, auto-generates if not specified)
- `--config, -f` - Config file path (default: `configs/base.yaml`)
- `--course, -c` - Course identifier (e.g., `BIOL101`)
- `--lecture, -l` - Lecture number (integer)

**Supported Video Formats:**
`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.m4v`, `.zoom`

**Examples:**
```bash
# Transcribe all videos in folder
corpus-video transcribe ./lectures --output transcript.md

# Transcribe with course info
corpus-video transcribe ./videos --course CS101 --lecture 5

# Custom config with specific model
corpus-video transcribe ./recordings -f whisper-config.yaml
```

#### `corpus-video clean`
Clean raw transcripts using LLM for better readability.

**Usage:**
```bash
corpus-video clean <TRANSCRIPT_FILE> [OPTIONS]
```

**Arguments:**
- `TRANSCRIPT_FILE` - Path to transcript file (required, must exist)

**Options:**
- `--output, -o` - Output file path (optional, auto-generates if not specified)
- `--config, -f` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Clean transcript
corpus-video clean raw_transcript.txt --output cleaned.md

# Auto-generated output path
corpus-video clean transcript.txt

# Custom cleaning model
corpus-video clean raw.txt -f cleaning-config.yaml
```

**Cleaning Features:**
- Removes filler words and hesitations
- Corrects grammar and punctuation
- Adds proper paragraph breaks
- Maintains original meaning and technical terms

#### `corpus-video augment`
Augment transcript with manual annotations and enhancements.

**Usage:**
```bash
corpus-video augment <TRANSCRIPT_FILE> [OPTIONS]
```

**Arguments:**
- `TRANSCRIPT_FILE` - Path to transcript file (required, must exist)

**Options:**
- `--output, -o` - Output file path (optional, auto-generates if not specified)
- `--config, -f` - Config file path (default: `configs/base.yaml`)
- `--auto` - Skip manual editing (flag)

**Examples:**
```bash
# Interactive augmentation
corpus-video augment cleaned.md --output final.md

# Auto-augmentation without manual review
corpus-video augment cleaned.md --auto

# Custom output path
corpus-video augment transcript.md -o enhanced_notes.md
```

#### `corpus-video pipeline`
Run complete video processing pipeline.

**Usage:**
```bash
corpus-video pipeline <INPUT_FOLDER> [OPTIONS]
```

**Arguments:**
- `INPUT_FOLDER` - Path to folder containing video files (required, must exist)

**Options:**
- `--output, -o` - Final output file path (optional)
- `--config, -f` - Config file path (default: `configs/base.yaml`)
- `--course, -c` - Course identifier (e.g., `CS101`)
- `--lecture, -l` - Lecture number (integer)
- `--skip-clean` - Skip cleaning step (flag)
- `--skip-augment` - Skip augmentation step (flag)

**Examples:**
```bash
# Full pipeline
corpus-video pipeline ./lecture_videos --course BIO101 --lecture 3

# Skip cleaning, output to specific file
corpus-video pipeline ./videos --skip-clean --output final_transcript.md

# Transcribe only
corpus-video pipeline ./recordings --skip-clean --skip-augment
```

**Pipeline Steps:**
1. **Transcribe**: Convert videos to text using Whisper
2. **Clean**: Improve readability using LLM (optional)
3. **Augment**: Add manual annotations (optional)
4. **Format**: Generate final structured output

---

## 6. corpus-orchestrate - Workflow Orchestrations

**Purpose**: Pre-composed workflows combining multiple tools for common use cases and comprehensive learning material generation.

### Commands

#### `corpus-orchestrate study-session`
Create comprehensive study materials from a collection.

**Usage:**
```bash
corpus-orchestrate study-session --collection <NAME> [OPTIONS]
```

**Options:**
- `--collection, -c` - Collection name (required)
- `--topic, -t` - Specific topic to focus on (optional)
- `--flashcards, -f` - Number of flashcards (default: 15)
- `--quiz, -q` - Number of quiz questions (default: 10)
- `--length, -l` - Summary length (`short`, `medium`, `long`, default: `medium`)
- `--output, -o` - Output file path (optional)
- `--config, -cfg` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Create study session
corpus-orchestrate study-session --collection biology --topic photosynthesis

# Custom counts and output
corpus-orchestrate study-session -c chemistry -f 25 -q 15 -o study_guide.md

# Short summary with focused topic
corpus-orchestrate study-session -c physics -t "quantum mechanics" -l short
```

**Generated Materials:**
1. Topic-focused summary
2. Flashcards for key concepts
3. Practice quiz questions
4. Combined study guide

#### `corpus-orchestrate lecture-pipeline`
Process lecture video into complete study materials.

**Usage:**
```bash
corpus-orchestrate lecture-pipeline <VIDEO_PATH> --course <NAME> --lecture <NUM> [OPTIONS]
```

**Arguments:**
- `VIDEO_PATH` - Path to lecture video file (required, must exist)

**Options:**
- `--course, -c` - Course identifier (required, e.g., `CS101`)
- `--lecture, -l` - Lecture number (required, integer)
- `--skip-clean` - Skip transcript cleaning (flag)
- `--output, -o` - Output file path (optional)
- `--config, -cfg` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Process lecture video
corpus-orchestrate lecture-pipeline lecture05.mp4 --course BIO101 --lecture 5

# Skip cleaning, custom output
corpus-orchestrate lecture-pipeline video.mp4 -c CS101 -l 3 --skip-clean -o materials.md

# Full processing pipeline
corpus-orchestrate lecture-pipeline recording.mp4 --course PHYS201 --lecture 12
```

**Pipeline includes:**
1. Video transcription
2. Transcript cleaning (optional)
3. RAG ingestion into course collection
4. Summary generation
5. Flashcard creation
6. Quiz generation
7. Consolidated study materials

#### `corpus-orchestrate build-kb`
Build knowledge base from documents.

**Usage:**
```bash
corpus-orchestrate build-kb <SOURCE_PATH> --collection <NAME> [OPTIONS]
```

**Arguments:**
- `SOURCE_PATH` - Path to documents (required, must exist)

**Options:**
- `--collection, -c` - Collection name (required)
- `--config, -cfg` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Build knowledge base from folder
corpus-orchestrate build-kb ./documents --collection course_materials

# Build from single file
corpus-orchestrate build-kb textbook.pdf --collection textbook

# Custom config
corpus-orchestrate build-kb ./papers -c research -cfg research.yaml
```

#### `corpus-orchestrate query-kb`
Query knowledge base with optional response generation.

**Usage:**
```bash
corpus-orchestrate query-kb --collection <NAME> <QUERY> [OPTIONS]
```

**Arguments:**
- `QUERY` - Query string (required)

**Options:**
- `--collection, -c` - Collection name (required)
- `--top-k, -k` - Number of results (default: 5)
- `--no-response` - Only retrieve chunks, don't generate response (flag)
- `--config, -cfg` - Config file path (default: `configs/base.yaml`)

**Examples:**
```bash
# Query with response generation
corpus-orchestrate query-kb -c notes "What is photosynthesis?"

# Retrieve chunks only
corpus-orchestrate query-kb -c research "neural networks" --no-response -k 10

# Custom retrieval count
corpus-orchestrate query-kb -c textbook "database normalization" -k 15
```

---

## 7. corpus-db - Database Management

**Purpose**: Comprehensive database backup, restore, migration, and export functionality for ChromaDB collections.

### Commands

#### `corpus-db list`
List all collections in the database.

**Usage:**
```bash
corpus-db list [OPTIONS]
```

**Global Options:**
- `--config, -c` - Configuration file path
- `--log-level` - Logging level (default: INFO)

**Examples:**
```bash
# List all collections
corpus-db list

# With custom config
corpus-db list --config production.yaml
```

**Output Format:**
```
Available Collections:
- biology_notes (245 documents)
- chemistry_flashcards (180 documents)
- physics_lectures (89 documents)
- research_papers (156 documents)
```

#### `corpus-db backup`
Backup a single collection to compressed archive.

**Usage:**
```bash
corpus-db backup <COLLECTION> --output <PATH> [OPTIONS]
```

**Arguments:**
- `COLLECTION` - Collection name to backup (required)

**Options:**
- `--output, -o` - Backup file path (required, .tar.gz format)
- `--no-metadata` - Exclude collection metadata (flag)

**Examples:**
```bash
# Backup collection
corpus-db backup notes --output backups/notes.tar.gz

# Backup without metadata
corpus-db backup research --output research_backup.tar.gz --no-metadata

# Daily backup with timestamp
corpus-db backup important --output "backups/important_$(date +%Y%m%d).tar.gz"
```

#### `corpus-db restore`
Restore collection from backup archive.

**Usage:**
```bash
corpus-db restore <BACKUP_FILE> [OPTIONS]
```

**Arguments:**
- `BACKUP_FILE` - Path to backup file (required, must exist)

**Options:**
- `--name` - New collection name (optional, uses original name if not specified)
- `--overwrite` - Overwrite existing collection (flag)

**Examples:**
```bash
# Restore collection
corpus-db restore backups/notes.tar.gz

# Restore with new name
corpus-db restore backup.tar.gz --name notes_v2

# Overwrite existing collection
corpus-db restore old_backup.tar.gz --overwrite
```

#### `corpus-db backup-all`
Backup all collections in the database.

**Usage:**
```bash
corpus-db backup-all --output-dir <PATH> [OPTIONS]
```

**Options:**
- `--output-dir, -o` - Backup directory (required)
- `--no-metadata` - Exclude metadata from all backups (flag)

**Examples:**
```bash
# Backup all collections
corpus-db backup-all --output-dir backups/

# Daily full backup
corpus-db backup-all -o "backups/$(date +%Y%m%d)/"

# Backup without metadata
corpus-db backup-all --output-dir emergency_backup/ --no-metadata
```

#### `corpus-db export`
Export collection in various data formats.

**Usage:**
```bash
corpus-db export <COLLECTION> --output <PATH> [OPTIONS]
```

**Arguments:**
- `COLLECTION` - Collection name to export (required)

**Options:**
- `--output, -o` - Export file path (required)
- `--format` - Export format (choices: `json`, `jsonl`, `csv`, default: `json`)
- `--include-embeddings` - Include embedding vectors (flag)

**Examples:**
```bash
# Export as JSON
corpus-db export notes --output exports/notes.json

# Export as CSV without embeddings
corpus-db export research --output data.csv --format csv

# Export with embeddings
corpus-db export vectors --output full_data.json --include-embeddings

# Export as JSONL for streaming
corpus-db export logs --output stream.jsonl --format jsonl
```

#### `corpus-db migrate`
Migrate data between collections.

**Usage:**
```bash
corpus-db migrate <SOURCE> <TARGET> [OPTIONS]
```

**Arguments:**
- `SOURCE` - Source collection name (required)
- `TARGET` - Target collection name (required)

**Options:**
- `--batch-size` - Number of documents per batch (default: 1000)

**Examples:**
```bash
# Migrate collection
corpus-db migrate old_notes new_notes

# Migrate with custom batch size
corpus-db migrate large_collection target --batch-size 500

# Migrate for reorganization
corpus-db migrate temp_storage permanent_storage
```

---

## 8. corpus-mcp-server - MCP Server

**Purpose**: Model Context Protocol server for AI agent integration, exposing all CorpusCallosum functionality via standardized protocol.

### Usage
```bash
corpus-mcp-server [OPTIONS]
```

### Options
- `--config, -c` - Configuration file path (optional)
- `--host` - Host to bind to (default: `0.0.0.0`)
- `--port` - Port to bind to (default: `8000`)
- `--transport` - Transport type (default: `streamable-http`)

### Examples

```bash
# Start with default settings
corpus-mcp-server

# Custom port and config
corpus-mcp-server --port 9000 --config production.yaml

# Bind to specific host
corpus-mcp-server --host localhost --port 8080

# Custom transport
corpus-mcp-server --transport http
```

### Health Endpoints
- `http://localhost:8000/health` - Basic health check
- `http://localhost:8000/health/ready` - Readiness check with database connectivity

### MCP Tools Exposed
- `rag_ingest` - Ingest documents into RAG collection
- `rag_query` - Query collection with response generation
- `rag_retrieve` - Retrieve document chunks only
- `generate_flashcards` - Create study flashcards
- `generate_summary` - Create document summaries
- `generate_quiz` - Create quiz questions
- `transcribe_video` - Transcribe video files
- `clean_transcript` - Clean raw transcripts

### MCP Resources
- `collections://list` - List all available collections
- `collection://{collection_name}` - Get specific collection information

### MCP Prompts
- `study_session_prompt` - Generate comprehensive study session
- `lecture_processing_prompt` - Process lecture video workflow

---

## Common Configuration Options

All CLI tools share common configuration patterns and can be customized through YAML configuration files.

### Global Configuration Structure
```yaml
# Base configuration (configs/base.yaml)
llm:
  endpoint: http://localhost:11434
  model: llama3
  backend: ollama                    # ollama | openai_compatible | anthropic_compatible
  timeout_seconds: 120.0
  temperature: 0.7
  max_tokens: null
  api_key: null
  fallback_models: []

embedding:
  backend: ollama                    # ollama | sentence-transformers
  model: nomic-embed-text
  dimensions: null

database:
  backend: chromadb
  mode: persistent                   # persistent | http
  host: localhost
  port: 8000
  persist_directory: ./chroma_store

paths:
  vault: ./vault                     # Document storage
  scratch_dir: ./scratch             # Temporary files
  output_dir: ./output               # Generated content
```

### Tool-Specific Configuration

#### RAG Configuration
```yaml
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

#### Flashcard Configuration
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

#### Video Configuration
```yaml
video:
  transcription:
    model: medium                    # Whisper model: tiny | base | small | medium | large
    language: auto                   # Language code or 'auto'
    device: auto                     # auto | cpu | cuda
  processing:
    chunk_size: 30                   # Seconds per chunk for processing
  collection_prefix: "video"         # Collection name prefix
```

### Environment Variables

Override any configuration value using environment variables with the `CC_` prefix:

```bash
# LLM Configuration
export CC_LLM_ENDPOINT=http://localhost:11434
export CC_LLM_MODEL=llama3
export CC_LLM_BACKEND=ollama
export CC_LLM_TEMPERATURE=0.7

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

### Common CLI Options

Most tools support these standard options:

- `--config, -f` - Configuration file path (default: `configs/base.yaml`)
- `--collection, -c` - Collection name (required for most operations)
- `--output, -o` - Output file path (optional, prints to stdout if not specified)
- `--help` - Show help message and exit

### Error Handling

All CLI tools provide:
- **Comprehensive error messages** with actionable suggestions
- **Input validation** with helpful error descriptions
- **Progress indicators** for long-running operations
- **Graceful interruption handling** (Ctrl+C)
- **Detailed logging output** with configurable verbosity

### Exit Codes

- `0` - Success
- `1` - General error (invalid arguments, configuration issues)
- `2` - File not found or permission errors
- `3` - Database connection errors
- `4` - LLM backend connection errors

### Performance Considerations

- **Chunking strategy**: Larger chunks provide more context but use more memory
- **Retrieval settings**: Higher `top_k` values improve recall but increase processing time
- **Model selection**: Larger models provide better quality but slower processing
- **Batch processing**: Use appropriate batch sizes for your available memory

### Troubleshooting

**Common Issues:**

1. **Database Connection Failed**
   - Check ChromaDB is running (for HTTP mode)
   - Verify file permissions (for persistent mode)
   - Check configuration settings

2. **LLM Connection Failed**
   - Verify Ollama is running and accessible
   - Check model is downloaded (`ollama pull llama3`)
   - Validate API endpoints and credentials

3. **Memory Issues**
   - Reduce chunk sizes in configuration
   - Lower `top_k` retrieval settings
   - Use smaller models for processing

4. **Slow Performance**
   - Enable GPU acceleration if available
   - Optimize chunking and retrieval parameters
   - Consider using faster models

This comprehensive tool usage guide provides all the information needed to effectively use CorpusCallosum's CLI interfaces for learning and knowledge management workflows.