# Code Quality & Linting Guide

This document describes how to maintain code quality and pass GitHub Actions checks.

## Quick Start

Before pushing to GitHub, run the linting and formatting script:

```bash
# Check all linting/formatting issues
python scripts/lint_and_format.py

# Auto-fix issues automatically
python scripts/lint_and_format.py --fix

# Run checks + tests
python scripts/lint_and_format.py --test

# Fix issues + run tests
python scripts/lint_and_format.py --fix --test
```

## What the Script Does

The `scripts/lint_and_format.py` script runs:

### 1. **Black** (Code Formatting)
- Enforces consistent code style across the entire codebase
- Formats to a standard style with 88-character line limit
- Auto-fix: `python -m black src/ tests/ scripts/`

### 2. **isort** (Import Sorting)
- Sorts imports in a consistent order
- Groups imports: stdlib → third-party → local
- Auto-fix: `python -m isort src/ tests/ scripts/`

### 3. **Ruff** (Fast Linting)
- Checks for:
  - Unused imports and variables
  - Undefined names
  - Syntax errors
  - Best practice violations
- Auto-fix: `python -m ruff check src/ tests/ scripts/ --fix`

### 4. **Trailing Whitespace**
- Detects lines with trailing spaces
- Must be fixed manually (editor auto-trim recommended)

### 5. **pytest** (Optional)
- Runs all unit and integration tests
- Use with: `python scripts/lint_and_format.py --test`

## Installation

The tools are already in `pyproject.toml`. Ensure you have the dependencies:

```bash
pip install black isort ruff pytest
```

## Common Issues & Fixes

### Black Format Violations
```bash
# Auto-format everything
python -m black src/ tests/ scripts/

# Check specific file
python -m black --check src/my_file.py
```

### Import Order Issues
```bash
# Auto-sort imports
python -m isort src/ tests/ scripts/

# Check specific file
python -m isort --check-only src/my_file.py
```

### Ruff Linting Errors
```bash
# Auto-fix common issues
python -m ruff check src/ tests/ scripts/ --fix

# View all issues
python -m ruff check src/ tests/ scripts/

# Fix specific rules (e.g., remove unused imports)
python -m ruff check src/ --select F401 --fix
```

### Trailing Whitespace
Most editors can auto-trim trailing whitespace:
- **VS Code**: Enable `files.trimTrailingWhitespace` in settings
- **PyCharm**: Code → Inspect Code → Run Cleanup
- **vim**: `:set list` then `:retab`

## GitHub Actions Configuration

The `.github/workflows/` directory contains CI/CD checks. These run:

1. `ruff check` — Fast linting
2. `black --check` — Verify formatting
3. `isort --check-only` — Verify import order
4. `pytest` — Run all tests
5. `mypy` (optional) — Type checking

## Pre-commit Hook Setup (Optional)

To automatically run checks before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Now checks run automatically on git commit
```

To bypass (use cautiously):
```bash
git commit --no-verify
```

## Best Practices

### While Coding
1. **Use an IDE with formatters**:
   - VS Code: Install Black Formatter extension
   - PyCharm: Enable Black formatting in settings

2. **Enable auto-format on save**:
   - Saves time and prevents linting errors

3. **Use type hints** (encouraged, not required):
   - Makes code more maintainable
   - Helps catch bugs early

### Before Pushing
```bash
# Complete pre-push checklist
python scripts/lint_and_format.py --fix --test

# Review changes
git status
git diff

# Then push
git push
```

### When CI Fails
1. Pull the latest changes
2. Run local lint/format check:
   ```bash
   python scripts/lint_and_format.py --fix
   ```
3. Commit the formatting fixes
4. Push again

## Disabling Specific Rules

If you need to disable a rule for a specific line:

```python
# Disable Black formatting for a line
x = 1  # fmt: skip

# Disable Ruff rules for a file
# ruff: noqa

# Disable specific Ruff rule for a line
unused_var = 5  # noqa: F841
```

Use sparingly — usually indicates the check is catching real issues.

## Troubleshooting

### "Module not found" errors when linting
Ensure all dependencies are installed:
```bash
pip install -e .
pip install -r requirements.txt
```

### Conflicts between formatters
- **Black** and **isort** can conflict on import formatting
- Solution: Use isort's Black-compatible profile (already configured)

### Line length too long after formatting
- Black has a hard limit of 88 characters
- If you have very long strings or URLs, consider:
  - Breaking into multiple lines
  - Using f-strings
  - Moving constants to module level

### Tests fail but linting passes
- Run tests locally:
  ```bash
  python -m pytest tests/ -v
  ```
- Check if you're using the right Python version (3.9+)

## See Also

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
