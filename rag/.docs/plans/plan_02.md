# Plan 02: CLI Commands for Easy Usage

## Goal

Add simple CLI commands that call Python functions directly (no server needed), preparing the codebase for future GUI integration.

## Current State

- `corpus-api` - starts the server
- `corpus-ingest` - CLI for ingestion (already exists)
- `corpus-setup` - interactive setup wizard

Basic usage requires curl commands with JSON formatting, which is error-prone.

## Proposed CLI Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `corpus-ask` | `corpus-ask "What is X?" -c notes` | Query a collection and stream answer |
| `corpus-flashcards` | `corpus-flashcards -c notes` | Generate flashcards from collection |
| `corpus-collections` | `corpus-collections` | List all collections |

## Implementation

### 1. Create `src/corpus_callosum/cli.py` (~100 lines)

```python
# Core functions:
# - ask_command() - query with streaming output to terminal
# - flashcards_command() - generate flashcards, print to terminal  
# - collections_command() - list collections
# - Clean argparse interfaces for each
```

### 2. Update `pyproject.toml`

Add entry points:
```toml
[project.scripts]
corpus-ask = "corpus_callosum.cli:ask_main"
corpus-flashcards = "corpus_callosum.cli:flashcards_main"
corpus-collections = "corpus_callosum.cli:collections_main"
```

### 3. Update `README.md`

Replace curl examples with simple CLI commands.

## Example Usage After Implementation

```bash
# Ingest (already exists)
corpus-ingest --path ./vault/biology --collection bio

# Ask a question (NEW)
corpus-ask "What is photosynthesis?" --collection bio

# Generate flashcards (NEW)  
corpus-flashcards --collection bio

# List collections (NEW)
corpus-collections
```

## CLI Interface Design

```bash
# corpus-ask
corpus-ask "question here" -c collection_name
corpus-ask "question here" --collection collection_name

# corpus-flashcards  
corpus-flashcards -c collection_name
corpus-flashcards --collection collection_name
corpus-flashcards -c bio --output flashcards.txt  # optional file output

# corpus-collections
corpus-collections          # plain list
corpus-collections --json   # JSON output for scripting
```

## Architecture for GUI Preparation

```
┌─────────────────────────────────────────────────────────┐
│                    Future GUI                            │
└─────────────────────┬───────────────────────────────────┘
                      │ imports
┌─────────────────────▼───────────────────────────────────┐
│              cli.py (thin CLI wrappers)                  │
│  - ask_main(), flashcards_main(), collections_main()    │
└─────────────────────┬───────────────────────────────────┘
                      │ calls
┌─────────────────────▼───────────────────────────────────┐
│              Core Library Functions                      │
│  - RagAgent().query()                                   │
│  - RagAgent().generate_flashcards()                     │
│  - HybridRetriever().list_collections()                 │
│  - Ingester().ingest_path()                             │
└─────────────────────────────────────────────────────────┘
```

The GUI will import and call the same core functions that the CLI uses, ensuring consistency and avoiding code duplication.

## Benefits

1. **Simpler usage** - No JSON formatting, no curl commands
2. **Less error-prone** - argparse handles validation
3. **No server required** - Works directly with local files
4. **GUI-ready** - Same Python functions can be called from GUI
5. **Scriptable** - Easy to use in shell scripts and automation

## Status

- [x] Create `cli.py` module
- [x] Add entry points to `pyproject.toml`
- [x] Update README with new CLI examples
- [x] Test all commands
