"""Storage abstraction for CorpusCallosum.

Provides unified interface for local and remote storage backends.
"""

from .base import StorageBackend, VectorDocument
from .local import LocalStorageBackend

__all__ = ["StorageBackend", "VectorDocument", "LocalStorageBackend"]
