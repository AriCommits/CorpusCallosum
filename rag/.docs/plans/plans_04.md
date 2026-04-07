# Plan 04: File Conversion Utility (`corpus-convert`)

## Overview

Create a CLI tool `corpus-convert` that converts various document formats to Markdown, with integration into `corpus-ingest` via a `--convert` flag.

## Problem Statement

Users have documents in various formats (PDF, DOCX, HTML, RTF) that they want to ingest into the RAG system. Currently, `corpus-ingest` only supports `.md`, `.txt`, and `.pdf` files. Users need an easy way to convert their documents to a format suitable for ingestion.

## CLI Commands

### Standalone Conversion
```bash
# Convert all supported files in a directory
corpus-convert /path/to/documents

# Dry-run to preview
corpus-convert /path/to/documents --dry-run
```

### Integrated with Ingest
```bash
# Default: scan, warn about unsupported files, suggest conversion
corpus-ingest --path /path/to/docs --collection MyDocs
# Output: "Warning: Found 3 .docx files that cannot be directly ingested.
#          Run: corpus-convert /path/to/docs
#          Then: corpus-ingest --path /path/to/docs/corpus_converted --collection MyDocs"

# With --convert flag: auto-convert first, then ingest the converted files
corpus-ingest --path /path/to/docs --collection MyDocs --convert
```

## Dependency Strategy: Minimal & Stable

| Format | Library | Why | Dependencies |
|--------|---------|-----|--------------|
| **PDF** | `pypdf` | Already installed, pure Python, actively maintained | 0 (existing) |
| **DOCX** | `python-docx` | Industry standard, 10+ years stable, pure Python | 1 new |
| **HTML** | `beautifulsoup4` + `markdownify` | BS4 is ubiquitous | 2 new |
| **TXT** | Built-in | No dependency needed | 0 |
| **RTF** | `striprtf` | Tiny (single file), no dependencies, stable | 1 new |

**Total new dependencies: 4** (`python-docx`, `beautifulsoup4`, `markdownify`, `striprtf`)

## File Structure

```
src/corpus_callosum/
├── convert.py              # Main converter + CLI
└── converters/
    ├── __init__.py         # Registry of converters
    ├── base.py             # BaseConverter ABC + ConversionResult
    ├── pdf.py              # PDF → MD
    ├── docx.py             # DOCX → MD  
    ├── html.py             # HTML → MD
    ├── rtf.py              # RTF → MD
    └── txt.py              # TXT → MD (minimal wrapper)

tests/
└── test_convert.py         # Unit tests
```

## Output Example

**Input:**
```
/path/to/documents/
├── notes.pdf
├── techniques.docx
├── readme.txt
├── Passing/
│   ├── guard.html
│   └── basics.rtf
└── unsupported.jpg  (ignored)
```

**After `corpus-convert /path/to/documents`:**
```
/path/to/documents/
├── (original files unchanged)
└── corpus_converted/
    ├── notes.md
    ├── techniques.md
    ├── readme.md
    ├── Passing_guard.md
    └── Passing_basics.md
```

## Implementation Details

### Core Components

1. **BaseConverter** - Abstract base class for all converters
2. **ConversionResult** - Dataclass for tracking conversion outcomes
3. **FileConverter** - Orchestrates scanning and conversion
4. **Individual Converters** - One per supported format

### Error Handling

- Failed conversions are logged as warnings
- Processing continues with remaining files
- Summary shows successes and failures

### Ingest Integration

- `corpus-ingest` scans for unsupported files first
- Warns user and suggests `corpus-convert` command
- `--convert` flag auto-converts before ingesting

## Test Plan

| Test | Description |
|------|-------------|
| `test_scan_directory_groups_by_extension` | Files correctly grouped |
| `test_flatten_filename` | `sub/dir/file.pdf` → `sub_dir_file.md` |
| `test_convert_pdf_extracts_text` | PDF text extraction works |
| `test_convert_docx_preserves_headings` | Headings become `#` syntax |
| `test_convert_html_removes_scripts` | Script/style tags removed |
| `test_convert_rtf_strips_formatting` | RTF → plain text |
| `test_convert_txt_passthrough` | TXT unchanged |
| `test_unsupported_files_skipped` | .jpg, .mp3 ignored |
| `test_error_continues_other_files` | One failure doesn't stop batch |
| `test_dry_run_no_files_written` | --dry-run is read-only |
| `test_output_dir_created` | Creates corpus_converted/ |
| `test_ingest_warns_unsupported` | Shows warning + command |
| `test_ingest_convert_flag` | --convert triggers conversion |

## Implementation Order

1. Create `converters/` directory and base class
2. Implement `txt.py` (simplest, test infrastructure)
3. Implement `pdf.py` (reuse existing logic)
4. Implement `docx.py`, `html.py`, `rtf.py`
5. Create `convert.py` with orchestration + CLI
6. Add entry point to `pyproject.toml`
7. Modify `ingest.py` for `--convert` flag and warnings
8. Write tests
9. Run tests, fix issues
10. Commit to GitHub
