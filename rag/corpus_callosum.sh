#!/bin/bash
# Corpus Callosum CLI - Bash wrapper script
#
# This script provides a bash interface to the Corpus Callosum Python CLI
# It activates the conda environment and forwards commands to the Python module
#
# Usage:
#   ./corpus_callosum.sh ask "query" --collection NAME [-k N]
#   ./corpus_callosum.sh sync pull --collection NAME
#   ./corpus_callosum.sh collections

set -euo pipefail

# Configuration
CONDA_ENV="cc"
DEFAULT_K=5

# Helper function to show usage
show_usage() {
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  ask          Query a collection"
    echo "  flashcards   Generate flashcards from a collection"
    echo "  collections  List all collections"
    echo "  ingest       Ingest documents into a collection"
    echo "  convert      Convert document formats"
    echo "  api          Start the API server"
    echo "  setup        Run initial setup"
    echo "  sync         Synchronize collections"
    echo ""
    echo "Examples:"
    echo "  $0 collections"
    echo "  $0 ask \"What is X?\" --collection docs"
    echo "  $0 ask \"What is X?\" --collection docs -k 10"
    echo "  $0 sync pull --collection docs"
    exit 1
}

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Miniconda or Anaconda." >&2
    exit 1
fi

# Check if at least one argument is provided
if [ $# -eq 0 ]; then
    show_usage
fi

# Activate conda environment and run Python CLI
# Note: We use 'conda run' instead of 'conda activate' for better script compatibility
exec conda run -n "$CONDA_ENV" python -m corpus_callosum "$@"
