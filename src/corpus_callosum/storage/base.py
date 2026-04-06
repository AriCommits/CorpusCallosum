"""Base storage backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class VectorDocument:
    """A document with its embedding and metadata."""

    id: str
    embedding: list[float]
    text: str
    metadata: dict[str, Any]
    checksum: str | None = None
    modified_at: datetime | None = None


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def get_collections(self) -> list[str]:
        """Get list of all collections."""
        pass

    @abstractmethod
    async def get_collection_metadata(self, collection: str) -> dict[str, Any]:
        """Get metadata for a collection."""
        pass

    @abstractmethod
    async def get_vectors(
        self, collection: str, ids: list[str] | None = None
    ) -> list[VectorDocument]:
        """Get vectors from collection.

        Args:
            collection: Collection name
            ids: Optional list of document IDs to retrieve. If None, get all.

        Returns:
            List of vector documents
        """
        pass

    @abstractmethod
    async def put_vectors(self, collection: str, vectors: list[VectorDocument]) -> None:
        """Store vectors in collection.

        Args:
            collection: Collection name
            vectors: List of vector documents to store
        """
        pass

    @abstractmethod
    async def delete_vectors(self, collection: str, ids: list[str]) -> None:
        """Delete vectors from collection.

        Args:
            collection: Collection name
            ids: List of document IDs to delete
        """
        pass

    @abstractmethod
    async def get_last_sync(self, collection: str) -> datetime | None:
        """Get last sync timestamp for collection.

        Args:
            collection: Collection name

        Returns:
            Last sync timestamp, or None if never synced
        """
        pass

    @abstractmethod
    async def set_last_sync(self, collection: str, timestamp: datetime) -> None:
        """Set last sync timestamp for collection.

        Args:
            collection: Collection name
            timestamp: Sync timestamp to record
        """
        pass

    @abstractmethod
    async def collection_exists(self, collection: str) -> bool:
        """Check if a collection exists.

        Args:
            collection: Collection name

        Returns:
            True if collection exists
        """
        pass
