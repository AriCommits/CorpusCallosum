# Technical Architecture Plan: CLI Synchronization & Dynamic Vector Retrieval

**Created:** Mon Apr 06 2026  
**Status:** Draft  
**Target Components:** Bash CLI, Python CLI, Query System

---

## Overview

This plan outlines the architecture for adding two major enhancements to the Corpus Callosum CLI tools:

1. **Synchronization Mechanism**: Enable both Bash and Python CLIs to sync collections, embeddings, and metadata between local storage and remote/cloud backends
2. **Dynamic Vector Retrieval**: Allow users to specify the number of vectors (`k`) to retrieve on a per-query basis via CLI arguments

---

## 1. Synchronization Mechanism

### 1.1 Goals

- [ ] Support bi-directional sync between local and remote storage
- [ ] Handle conflicts gracefully (last-write-wins, versioning, or merge strategies)
- [ ] Provide sync status and progress feedback
- [ ] Support partial sync (by collection, by date range, etc.)
- [ ] Ensure atomicity and data integrity during sync operations

### 1.2 Architecture

#### 1.2.1 Storage Abstraction Layer

Create a unified storage interface that abstracts local and remote backends:

```python
# corpus_callosum/storage/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def get_collections(self) -> List[str]:
        """Get list of all collections"""
        pass
    
    @abstractmethod
    async def get_collection_metadata(self, collection: str) -> Dict[str, Any]:
        """Get metadata for a collection"""
        pass
    
    @abstractmethod
    async def get_vectors(self, collection: str, ids: Optional[List[str]] = None) -> List[Dict]:
        """Get vectors from collection"""
        pass
    
    @abstractmethod
    async def put_vectors(self, collection: str, vectors: List[Dict]) -> None:
        """Store vectors in collection"""
        pass
    
    @abstractmethod
    async def delete_vectors(self, collection: str, ids: List[str]) -> None:
        """Delete vectors from collection"""
        pass
    
    @abstractmethod
    async def get_last_sync(self, collection: str) -> Optional[datetime]:
        """Get last sync timestamp for collection"""
        pass
    
    @abstractmethod
    async def set_last_sync(self, collection: str, timestamp: datetime) -> None:
        """Set last sync timestamp for collection"""
        pass
```

#### 1.2.2 Sync Engine

Implement a synchronization engine that orchestrates sync operations:

```python
# corpus_callosum/sync/engine.py
from enum import Enum
from typing import Optional, List
from datetime import datetime

class SyncDirection(Enum):
    PULL = "pull"  # Remote -> Local
    PUSH = "push"  # Local -> Remote
    BIDIRECTIONAL = "bidirectional"  # Both directions

class SyncStrategy(Enum):
    LAST_WRITE_WINS = "last_write_wins"
    MANUAL_RESOLVE = "manual_resolve"
    KEEP_BOTH = "keep_both"

class SyncEngine:
    def __init__(self, local: StorageBackend, remote: StorageBackend):
        self.local = local
        self.remote = remote
    
    async def sync(
        self, 
        collection: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        strategy: SyncStrategy = SyncStrategy.LAST_WRITE_WINS,
        force: bool = False
    ) -> SyncResult:
        """
        Synchronize a collection between local and remote storage
        
        Args:
            collection: Collection name to sync
            direction: Sync direction (pull, push, or bidirectional)
            strategy: Conflict resolution strategy
            force: Force sync even if conflicts exist
        
        Returns:
            SyncResult with statistics and status
        """
        pass
    
    async def sync_all(self, **kwargs) -> Dict[str, SyncResult]:
        """Sync all collections"""
        pass
    
    async def get_diff(self, collection: str) -> SyncDiff:
        """Get differences between local and remote"""
        pass
```

#### 1.2.3 CLI Integration

**Python CLI:**

```bash
# Sync commands
python -m corpus_callosum sync pull --collection CARS
python -m corpus_callosum sync push --collection CARS
python -m corpus_callosum sync --collection CARS  # bidirectional
python -m corpus_callosum sync --all  # sync all collections
python -m corpus_callosum sync status --collection CARS
python -m corpus_callosum sync diff --collection CARS

# Sync options
python -m corpus_callosum sync --collection CARS --strategy last_write_wins
python -m corpus_callosum sync --collection CARS --force
python -m corpus_callosum sync --collection CARS --remote s3://my-bucket/cc-data
```

**Bash CLI:**

```bash
# Sync commands
./corpus_callosum.sh sync pull --collection CARS
./corpus_callosum.sh sync push --collection CARS
./corpus_callosum.sh sync --collection CARS  # bidirectional
./corpus_callosum.sh sync --all
./corpus_callosum.sh sync status --collection CARS
./corpus_callosum.sh sync diff --collection CARS
```

### 1.3 Implementation Checklist

- [ ] Create storage abstraction base class (`StorageBackend`)
- [ ] Implement `LocalStorageBackend` (file system, SQLite, etc.)
- [ ] Implement `RemoteStorageBackend` (S3, GCS, HTTP API, etc.)
- [ ] Create `SyncEngine` class with diff/merge logic
- [ ] Implement conflict resolution strategies
- [ ] Add sync metadata tracking (timestamps, versions)
- [ ] Create CLI argument parser for sync commands (Python)
- [ ] Create CLI argument parser for sync commands (Bash)
- [ ] Add progress reporting for long sync operations
- [ ] Write unit tests for sync engine
- [ ] Write integration tests for end-to-end sync
- [ ] Add sync command documentation
- [ ] Handle edge cases (network failures, partial syncs, interrupted syncs)

### 1.4 Remote Backend Options

Support multiple remote backends:

- **S3/GCS**: Object storage for embeddings and metadata
- **HTTP API**: RESTful API for centralized corpus server
- **Git-based**: Use Git LFS for version control
- **Database**: PostgreSQL with pgvector, Pinecone, Weaviate, etc.

### 1.5 Data Format

Use a consistent data format for sync operations:

```json
{
  "collection": "CARS",
  "version": "1.0",
  "last_modified": "2026-04-06T10:30:00Z",
  "vectors": [
    {
      "id": "doc_001",
      "embedding": [0.1, 0.2, ...],
      "metadata": {
        "text": "Tesla Model 3",
        "source": "manual_entry",
        "created_at": "2026-04-01T08:00:00Z"
      },
      "checksum": "sha256:abc123..."
    }
  ]
}
```

---

## 2. Dynamic Vector Retrieval (`-k` Parameter)

### 2.1 Goals

- [ ] Allow users to specify number of vectors to retrieve per query
- [ ] Support both Python and Bash CLIs
- [ ] Maintain backward compatibility with default behavior
- [ ] Validate `k` parameter (must be positive integer)
- [ ] Update query logic to respect `k` parameter

### 2.2 Architecture

#### 2.2.1 Query Engine Update

Modify the query/search functions to accept a `top_k` parameter:

```python
# corpus_callosum/query/engine.py
from typing import List, Dict, Any, Optional

class QueryEngine:
    def __init__(self, collection: str, default_k: int = 5):
        self.collection = collection
        self.default_k = default_k
    
    def query(
        self, 
        query_text: str, 
        k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the collection and return top-k results
        
        Args:
            query_text: The query string
            k: Number of results to return (defaults to self.default_k)
            filter_metadata: Optional metadata filters
        
        Returns:
            List of top-k matching documents with scores
        """
        k = k or self.default_k
        
        # Validate k
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        # Generate embedding for query
        query_embedding = self.embed(query_text)
        
        # Search collection
        results = self.search(
            query_embedding, 
            top_k=k,
            filter_metadata=filter_metadata
        )
        
        return results
```

#### 2.2.2 CLI Integration

**Python CLI:**

```bash
# Query with default k (e.g., 5)
python -m corpus_callosum ask "What are electric cars?" --collection CARS

# Query with custom k
python -m corpus_callosum ask "What are electric cars?" --collection CARS -k 10
python -m corpus_callosum ask "What are electric cars?" --collection CARS --top-k 10

# Query with k=1 (single best match)
python -m corpus_callosum ask "What are electric cars?" --collection CARS -k 1

# Query with filters and custom k
python -m corpus_callosum ask "Sports cars" --collection CARS -k 20 --filter "type=sports"
```

**Bash CLI:**

```bash
# Query with default k
./corpus_callosum.sh ask "What are electric cars?" --collection CARS

# Query with custom k
./corpus_callosum.sh ask "What are electric cars?" --collection CARS -k 10
./corpus_callosum.sh ask "What are electric cars?" --collection CARS --top-k 10
```

#### 2.2.3 Argument Parser Updates

**Python (`corpus_callosum/__main__.py` or `cli.py`):**

```python
import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="Corpus Callosum CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Ask/Query command
    ask_parser = subparsers.add_parser("ask", help="Query a collection")
    ask_parser.add_argument("query", type=str, help="Query text")
    ask_parser.add_argument("--collection", "-c", required=True, help="Collection name")
    ask_parser.add_argument(
        "-k", "--top-k", 
        type=int, 
        default=5, 
        help="Number of results to return (default: 5)"
    )
    ask_parser.add_argument("--filter", type=str, help="Metadata filter")
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "ask":
        engine = QueryEngine(collection=args.collection)
        results = engine.query(args.query, k=args.top_k)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. [Score: {result['score']:.3f}] {result['text']}")
```

**Bash (`corpus_callosum.sh`):**

```bash
#!/bin/bash

# Default values
DEFAULT_K=5

# Parse arguments
COMMAND=""
QUERY=""
COLLECTION=""
TOP_K=$DEFAULT_K

while [[ $# -gt 0 ]]; do
    case $1 in
        ask)
            COMMAND="ask"
            shift
            QUERY="$1"
            shift
            ;;
        --collection|-c)
            COLLECTION="$2"
            shift 2
            ;;
        -k|--top-k)
            TOP_K="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Validate inputs
if [[ -z "$COMMAND" ]] || [[ -z "$QUERY" ]] || [[ -z "$COLLECTION" ]]; then
    echo "Usage: $0 ask \"query\" --collection COLLECTION [-k N]"
    exit 1
fi

# Execute query
if [[ "$COMMAND" == "ask" ]]; then
    # Activate conda environment and run Python CLI with k parameter
    conda activate cc
    python -m corpus_callosum ask "$QUERY" --collection "$COLLECTION" -k "$TOP_K"
fi
```

### 2.3 Implementation Checklist

- [ ] Update `QueryEngine` class to accept `k` parameter
- [ ] Modify search/retrieval logic to respect `k`
- [ ] Add validation for `k` (must be positive integer)
- [ ] Update Python CLI argument parser to accept `-k` / `--top-k`
- [ ] Update Bash CLI script to accept `-k` / `--top-k`
- [ ] Set sensible default value for `k` (e.g., 5)
- [ ] Update help messages and documentation
- [ ] Add unit tests for query with different `k` values
- [ ] Add integration tests for CLI with `-k` parameter
- [ ] Update user documentation and examples

### 2.4 Configuration

Allow users to set default `k` in configuration file:

```yaml
# corpus_callosum.yaml
query:
  default_k: 5  # Default number of results
  max_k: 100    # Maximum allowed k value

collections:
  CARS:
    default_k: 10  # Collection-specific default
```

---

## 3. Integration & Testing

### 3.1 Testing Strategy

- [ ] Unit tests for storage backends
- [ ] Unit tests for sync engine (diff, merge, conflict resolution)
- [ ] Unit tests for query engine with varying `k`
- [ ] Integration tests for CLI commands (Python & Bash)
- [ ] End-to-end tests for sync workflows
- [ ] Performance tests for large collections
- [ ] Edge case tests (network failures, corrupted data, etc.)

### 3.2 Documentation

- [ ] Update README with sync commands
- [ ] Update README with `-k` parameter examples
- [ ] Create sync tutorial/guide
- [ ] Add API documentation for storage backends
- [ ] Add troubleshooting guide for sync issues
- [ ] Update CLI help text

### 3.3 Backward Compatibility

- [ ] Ensure existing commands work without changes
- [ ] Default `k` value maintains current behavior
- [ ] Sync is opt-in (doesn't affect existing workflows)
- [ ] Configuration file is optional

---

## 4. Implementation Phases

### Phase 1: Dynamic Vector Retrieval (Quick Win)
**Estimated Time:** 2-3 days

1. Update query engine to accept `k` parameter
2. Update Python CLI argument parser
3. Update Bash CLI script
4. Add tests and documentation

### Phase 2: Storage Abstraction
**Estimated Time:** 3-5 days

1. Create `StorageBackend` base class
2. Implement `LocalStorageBackend`
3. Implement initial `RemoteStorageBackend` (e.g., S3)
4. Add tests

### Phase 3: Sync Engine
**Estimated Time:** 5-7 days

1. Implement `SyncEngine` with basic diff/merge
2. Add conflict resolution strategies
3. Add sync metadata tracking
4. Implement progress reporting
5. Add tests

### Phase 4: CLI Integration
**Estimated Time:** 2-3 days

1. Add sync commands to Python CLI
2. Add sync commands to Bash CLI
3. Integrate with conda environment activation
4. Add tests and documentation

### Phase 5: Polish & Advanced Features
**Estimated Time:** 3-5 days

1. Add additional remote backends
2. Optimize sync for large collections
3. Add advanced sync options (partial sync, incremental sync)
4. Comprehensive testing and bug fixes
5. Complete documentation

---

## 5. Dependencies & Prerequisites

- [ ] Python 3.8+ with asyncio support
- [ ] Miniconda environment `cc` configured
- [ ] Storage library (e.g., `boto3` for S3, `google-cloud-storage` for GCS)
- [ ] Vector database client libraries (if using remote vector DB)
- [ ] CLI argument parsing library (already using `argparse`)
- [ ] Testing framework (pytest)

---

## 6. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss during sync | High | Implement atomic operations, checksums, and backup before sync |
| Network failures mid-sync | Medium | Add retry logic, resume capability, and transaction logs |
| Conflict resolution complexity | Medium | Start with simple last-write-wins, add advanced strategies later |
| Performance degradation with large collections | Medium | Implement incremental sync, compression, and parallel transfers |
| Breaking existing workflows | High | Maintain backward compatibility, make sync opt-in |

---

## 7. Success Metrics

- [ ] Users can sync collections between local and remote with a single command
- [ ] Users can specify `-k` parameter to control result count
- [ ] Sync operations complete without data loss
- [ ] CLI commands work seamlessly in both Python and Bash
- [ ] Performance remains acceptable for collections up to 100k vectors
- [ ] Documentation is clear and comprehensive

---

## Next Steps

1. Review and approve this plan
2. Set up development environment with conda `cc`
3. Begin Phase 1 implementation (dynamic vector retrieval)
4. Conduct code reviews after each phase
5. Deploy and gather user feedback
