"""Simple test to verify imports work correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from corpus_callosum.config import BaseConfig, load_config
    from corpus_callosum.db import ChromaDBBackend, DatabaseBackend

    print("✓ Configuration imports work")
    print("✓ Database imports work")

    # Test config creation
    config = BaseConfig()
    print(f"✓ BaseConfig created: LLM model = {config.llm.model}")

    print("\nAll imports successful!")
    sys.exit(0)

except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
