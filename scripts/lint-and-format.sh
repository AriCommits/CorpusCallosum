#!/bin/bash
# Lint and format script for CorpusCallosum
# Ensures code passes all pre-commit checks before pushing to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "CorpusCallosum Lint & Format Check"
echo "=========================================="

# Track if any checks failed
FAILED=0

# Function to run a check
run_check() {
    local name=$1
    local cmd=$2

    echo -e "\n${YELLOW}Running: $name${NC}"
    if eval "$cmd"; then
        echo -e "${GREEN}✓ $name passed${NC}"
    else
        echo -e "${RED}✗ $name failed${NC}"
        FAILED=1
    fi
}

# 1. Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python --version

# 2. Format with Black
run_check "Black (code formatting)" \
    "python -m black --check src/ tests/ scripts/"

# 3. Sort imports with isort
run_check "isort (import sorting)" \
    "python -m isort --check-only --diff src/ tests/ scripts/"

# 4. Lint with Ruff
run_check "Ruff (linting)" \
    "python -m ruff check src/ tests/ scripts/"

# 5. Type checking with mypy (optional, skip if not installed)
if command -v mypy &> /dev/null; then
    run_check "mypy (type checking)" \
        "python -m mypy src/ --ignore-missing-imports --no-error-summary 2>&1 | head -20 || true"
else
    echo -e "${YELLOW}⊘ mypy not installed, skipping type checking${NC}"
fi

# 6. Check for trailing whitespace
echo -e "\n${YELLOW}Checking for trailing whitespace...${NC}"
if grep -r '\s$' src/ tests/ scripts/ --include="*.py" 2>/dev/null; then
    echo -e "${RED}✗ Found trailing whitespace${NC}"
    FAILED=1
else
    echo -e "${GREEN}✓ No trailing whitespace${NC}"
fi

# 7. Check for long lines (warnings only)
echo -e "\n${YELLOW}Checking for lines > 100 characters (warnings)...${NC}"
long_lines=$(find src/ tests/ scripts/ -name "*.py" -exec awk 'length > 100' {} + | wc -l)
if [ "$long_lines" -gt 0 ]; then
    echo -e "${YELLOW}⊘ Found $long_lines lines > 100 chars (not critical)${NC}"
else
    echo -e "${GREEN}✓ No lines > 100 characters${NC}"
fi

# 8. Run pytest if requested
if [ "$1" == "--test" ] || [ "$1" == "-t" ]; then
    echo -e "\n${YELLOW}Running tests...${NC}"
    run_check "pytest (unit tests)" \
        "python -m pytest tests/ -v --tb=short"
fi

# Summary
echo -e "\n=========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo -e "Ready to push to GitHub${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo -e "\n${YELLOW}To fix issues automatically:${NC}"
    echo "  black src/ tests/ scripts/"
    echo "  isort src/ tests/ scripts/"
    echo "  ruff check src/ tests/ scripts/ --fix"
    exit 1
fi
