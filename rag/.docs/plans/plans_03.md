# Plan 03: Allow Arbitrary Path Ingestion for CLI

## Problem Statement

The `corpus-ingest` CLI currently restricts document ingestion to files within the configured vault directory. This prevents users from ingesting documents from arbitrary paths on their filesystem, such as:

```bash
corpus-ingest --path /Users/arian/Desktop/Jujistu --collection JJ
# Error: Path /Users/arian/Desktop/Jujistu is outside the allowed vault directory
```

The user expects to be able to specify any valid directory path and have the RAG agent work correctly with documents from that location.

## Root Cause Analysis

The restriction is in `src/corpus_callosum/ingest.py` lines 61-67:

```python
resolved_path = source.resolve()
vault_path = self.config.paths.vault.resolve()
if os.path.commonpath([resolved_path, vault_path]) != str(vault_path):
    raise ValueError(
        f"Path {source} is outside the allowed vault directory ({vault_path}). "
        f"Only files within the vault directory can be ingested."
    )
```

This check was likely added as a security measure, but it's overly restrictive for legitimate use cases where users want to ingest documents from different locations.

## Design Considerations

### Option A: Remove the restriction entirely
- **Pros**: Maximum flexibility, simplest implementation
- **Cons**: None for local CLI usage; the RAG agent and retriever don't depend on files being in the vault

### Option B: Make the restriction configurable
- **Pros**: Allows security-conscious deployments to keep the restriction
- **Cons**: More complex, adds configuration overhead

### Option C: Add a `--allow-any-path` flag
- **Pros**: Explicit user consent to ingest from outside vault
- **Cons**: Extra friction for users, flag feels unnecessary

## Recommendation

**Option A: Remove the restriction entirely**

Rationale:
1. The RAG system stores document content in ChromaDB vectors - it doesn't read from the original files after ingestion
2. The `source_file` metadata is purely informational (for citations)
3. Collection names already namespace the documents properly
4. The vault directory concept is more relevant for serving files, not ingestion
5. Users should be able to organize their source materials however they prefer

## Implementation Plan

### 1. Modify `src/corpus_callosum/ingest.py`

Remove the vault directory check (lines 61-67) in the `ingest_path` method:

```python
def ingest_path(self, path: str | Path, collection_name: str) -> IngestResult:
    source = Path(path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Path does not exist: {source}")
    if not collection_name.strip():
        raise ValueError("collection_name cannot be empty")
    
    # REMOVE: vault directory restriction check
    
    files = list(self._iter_source_files(source))
    ...
```

### 2. Update Tests (if any exist that test the restriction)

Verify no tests depend on this restriction behavior. If tests exist that validate the vault restriction, they should be removed.

### 3. Verify Existing Functionality

After the change:
- Ingestion from vault directory should still work
- Ingestion from any valid path should now work
- ChromaDB storage and retrieval should function normally
- The RAG agent should query collections regardless of original source path

## Files to Modify

| File | Change |
|------|--------|
| `src/corpus_callosum/ingest.py` | Remove vault path restriction (lines 61-67) |

## Testing

```bash
# Test ingestion from arbitrary path
corpus-ingest --path /Users/arian/Desktop/Jujistu --collection JJ

# Verify the collection was created and is queryable
# (via API or direct ChromaDB inspection)
```

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| User accidentally ingests sensitive files | User is explicitly specifying paths - they control what gets ingested |
| Path traversal attacks | Not applicable - this is a local CLI tool, not a web API |

## Rollback Plan

If issues arise, restore the vault directory check in `ingest.py`. The change is isolated to a single code block.
