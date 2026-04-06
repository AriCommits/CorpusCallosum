"""Local storage backend using ChromaDB."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..chroma import create_chroma_client
from ..config import Config, get_config
from .base import StorageBackend, VectorDocument


class LocalStorageBackend(StorageBackend):
    """Local storage backend using ChromaDB and filesystem for metadata."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or get_config()
        self.client = create_chroma_client(self.config)
        self._metadata_dir = self.config.paths.chromadb_store / "sync_metadata"
        self._metadata_dir.mkdir(parents=True, exist_ok=True)

    def _get_sync_metadata_path(self, collection: str) -> Path:
        """Get path to sync metadata file for a collection."""
        return self._metadata_dir / f"{collection}.json"

    async def get_collections(self) -> list[str]:
        """Get list of all collections."""
        collections = self.client.list_collections()
        return [col.name for col in collections]

    async def get_collection_metadata(self, collection: str) -> dict[str, Any]:
        """Get metadata for a collection."""
        try:
            col = self.client.get_collection(name=collection)
            return {
                "name": collection,
                "count": col.count(),
            }
        except Exception:
            return {}

    async def get_vectors(
        self, collection: str, ids: list[str] | None = None
    ) -> list[VectorDocument]:
        """Get vectors from collection."""
        try:
            col = self.client.get_collection(name=collection)
        except Exception:
            return []

        if ids is None:
            # Get all documents
            result = col.get(include=["embeddings", "documents", "metadatas"])
        else:
            # Get specific documents
            result = col.get(ids=ids, include=["embeddings", "documents", "metadatas"])

        doc_ids = result.get("ids", [])
        embeddings = result.get("embeddings", [])
        documents = result.get("documents", [])
        metadatas = result.get("metadatas", [])

        vectors: list[VectorDocument] = []
        for i, doc_id in enumerate(doc_ids):
            embedding = embeddings[i] if i < len(embeddings) else []
            text = documents[i] if i < len(documents) else ""
            metadata = metadatas[i] if i < len(metadatas) else {}

            # Calculate checksum
            checksum = self._calculate_checksum(embedding, text, metadata)

            # Try to get modified_at from metadata
            modified_at = None
            if metadata and "modified_at" in metadata:
                try:
                    modified_at = datetime.fromisoformat(metadata["modified_at"])
                except (ValueError, TypeError):
                    pass

            vectors.append(
                VectorDocument(
                    id=doc_id,
                    embedding=embedding,
                    text=text,
                    metadata=metadata,
                    checksum=checksum,
                    modified_at=modified_at,
                )
            )

        return vectors

    async def put_vectors(self, collection: str, vectors: list[VectorDocument]) -> None:
        """Store vectors in collection."""
        try:
            col = self.client.get_collection(name=collection)
        except Exception:
            # Create collection if it doesn't exist
            col = self.client.create_collection(name=collection)

        if not vectors:
            return

        ids = [v.id for v in vectors]
        embeddings = [v.embedding for v in vectors]
        documents = [v.text for v in vectors]
        metadatas = []

        for v in vectors:
            metadata = dict(v.metadata) if v.metadata else {}
            # Add modified timestamp
            if v.modified_at:
                metadata["modified_at"] = v.modified_at.isoformat()
            else:
                metadata["modified_at"] = datetime.now().isoformat()
            metadatas.append(metadata)

        col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    async def delete_vectors(self, collection: str, ids: list[str]) -> None:
        """Delete vectors from collection."""
        if not ids:
            return

        try:
            col = self.client.get_collection(name=collection)
            col.delete(ids=ids)
        except Exception:
            pass

    async def get_last_sync(self, collection: str) -> datetime | None:
        """Get last sync timestamp for collection."""
        metadata_path = self._get_sync_metadata_path(collection)
        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_sync_str = data.get("last_sync")
                if last_sync_str:
                    return datetime.fromisoformat(last_sync_str)
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    async def set_last_sync(self, collection: str, timestamp: datetime) -> None:
        """Set last sync timestamp for collection."""
        metadata_path = self._get_sync_metadata_path(collection)

        # Load existing metadata
        data = {}
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Update last_sync
        data["last_sync"] = timestamp.isoformat()

        # Write back
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    async def collection_exists(self, collection: str) -> bool:
        """Check if a collection exists."""
        try:
            self.client.get_collection(name=collection)
            return True
        except Exception:
            return False

    def _calculate_checksum(
        self, embedding: list[float], text: str, metadata: dict[str, Any]
    ) -> str:
        """Calculate SHA256 checksum for a vector document."""
        content = {
            "embedding": embedding,
            "text": text,
            "metadata": {k: v for k, v in metadata.items() if k != "modified_at"},
        }
        serialized = json.dumps(content, sort_keys=True)
        return f"sha256:{hashlib.sha256(serialized.encode()).hexdigest()}"
