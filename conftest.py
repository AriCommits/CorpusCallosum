"""Root conftest: ensure src/ is on sys.path for all tests."""

import sys
from pathlib import Path

# Add src to path so package imports work without installation
src = Path(__file__).parent / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
