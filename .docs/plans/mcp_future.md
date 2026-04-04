# Future MCP Integration Plan

This plan documents the work previously implemented for MCP (Model Context Protocol) integration,
which was removed in favor of a REST-only approach. It serves as a blueprint for future re-implementation.

## Context

MCP was initially implemented to expose CorpusCallosum capabilities to AI clients like Claude Desktop,
Cursor, and Windsurf. It was removed to simplify the codebase and consolidate all functionality behind
the REST API. This plan preserves the design decisions and implementation details for when MCP is
re-introduced.

## Architecture

### Transport Modes

Two transport modes, one codebase:

1. **stdio server** — Primary. Claude Desktop, Cursor, Windsurf connect via stdio. Imports `RagAgent`/`Ingester` directly — no HTTP overhead.
2. **HTTP/SSE endpoint** — Secondary. Adds `/mcp/sse` route to the existing FastAPI app for remote clients.

### Tools to Expose

| Tool | Description | Inputs |
|------|-------------|--------|
| `query_documents` | Query a collection with RAG | `query`, `collection`, `model?`, `session_id?` |
| `ingest_documents` | Ingest files/directories into a collection | `file_path`, `collection` |
| `list_collections` | List all available collections | *(none)* |
| `critique_writing` | Get AI writing feedback | `essay_text`, `model?` |
| `generate_flashcards` | Generate study flashcards | `collection`, `model?` |
| `summarize_collection` | Summarize collection content | `collection`, `detail_level?` |

### Resources to Expose (read-only data)

| Resource | URI Template | Description |
|----------|-------------|-------------|
| Collection contents | `collection://{name}` | All documents in a collection |
| Collection metadata | `collection://{name}/meta` | Size, source files, etc. |

### File Structure

```
src/corpus_callosum/
  mcp/
    __init__.py
    server.py       # MCP server setup (stdio + HTTP transports)
    tools.py        # Tool definitions (shared logic)
    resources.py    # Resource definitions
```

## Implementation Steps

### Step 1: Re-create MCP Module

1. Create `src/corpus_callosum/mcp/` directory
2. Create `tools.py` — Define all 6 tools with JSON schemas, delegate to `RagAgent` and `Ingester`
3. Create `resources.py` — Define collection resources
4. Create `server.py` — Wire up stdio + HTTP transports, config loading
5. Create `__init__.py` — Public exports

### Step 2: Add MCP Dependency

1. Add `mcp` package to `requirements.txt` and `pyproject.toml` optional dependencies
2. Add `mcp.*` to mypy overrides
3. Add `corpus-mcp` entry point to `pyproject.toml`

### Step 3: Integrate with API

1. Add `/mcp` route to `api.py` — Mount HTTP transport on existing FastAPI
2. Add `mcp` section to config schema (enabled, transport, port)
3. Add config examples for MCP settings

### Step 4: Security (Critical — Was Missing Before)

1. **API key authentication on MCP HTTP transport** — Same middleware as REST API
2. **Rate limiting on MCP server** — Same rate limiter as REST API
3. **Input validation on all MCP tool parameters** — Validate collection names, file paths, etc.
4. **Vault-backed secret access** — MCP tools should use Vault for secrets, not config files

### Step 5: Client Integration

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "corpus-callosum": {
      "command": "corpus-mcp",
      "args": ["--config", "/path/to/corpus_callosum.yaml"]
    }
  }
}
```

**Cursor / Windsurf** — Same stdio config via their MCP settings UI.

## Design Decisions

### Direct Import vs HTTP Proxy

Direct import is faster and simpler but couples the MCP server to the Python codebase. HTTP proxy
would work across language boundaries but adds latency and complexity. **Recommendation: direct import**
since everything is Python-local.

### Streaming Responses

MCP tools return complete results, not streams. The SSE token streaming from the API won't work over
MCP — responses will be collected and returned as a single string. This is fine for tool use since
the LLM client handles the streaming.

### Security Model

The stdio server inherits the same config-based auth. For local use (Claude Desktop), auth can be
disabled. For HTTP transport, it reuses the existing API key middleware.

## Future Improvements

1. **Streaming MCP tools** — If the MCP spec adds streaming tool responses, integrate with existing SSE
2. **MCP prompts** — Expose pre-built prompts (e.g., "generate study guide from collection")
3. **MCP sampling** — Let the MCP server make LLM calls on behalf of the client
4. **Vault integration** — MCP tools authenticate to Vault for secrets instead of config files
5. **Multi-collection queries** — Tool that queries across multiple collections simultaneously
6. **Collection management** — Tools to delete, rename, or merge collections

## Reference: Previous Implementation

The following files contained the original implementation (now deleted):

- `src/corpus_callosum/mcp/__init__.py` — Module exports
- `src/corpus_callosum/mcp/tools.py` — 6 tool definitions using `@mcp.tool()` decorator
- `src/corpus_callosum/mcp/resources.py` — 2 resource definitions using `@mcp.resource()` decorator
- `src/corpus_callosum/mcp/server.py` — FastMCP server with stdio + HTTP transports, `mount_mcp()` function

The implementation used the `mcp` Python SDK's `FastMCP` class with `@mcp.tool()` and
`@mcp.resource()` decorators. It delegated to existing `RagAgent`, `Ingester`, and
`HybridRetriever` instances.

## Config Schema (Proposed)

```yaml
mcp:
  enabled: false
  transport: http  # "stdio" or "http"
  port: 8081