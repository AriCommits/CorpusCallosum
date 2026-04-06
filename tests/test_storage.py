"""Tests for storage backends."""

import pytest
from datetime import datetime
from corpus_callosum.storage.base import VectorDocument, StorageBackend
from corpus_callosum.storage.local import LocalStorageBackend
from corpus_callosum.config import Config


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock config with temporary paths."""
    # This would normally use the full Config, but for testing we'll mock it
    class MockConfig:
        class Paths:
            def __init__(self, chromadb_store):
                self.chromadb_store = chromadb_store

        class ChromaConfig:
            mode = "persistent"
            host = "localhost"
            port = 8000
            ssl = False

        def __init__(self, tmp_path):
            self.paths = self.Paths(tmp_path / "chroma_test")
            self.chroma = self.ChromaConfig()

    return MockConfig(tmp_path)


@pytest.fixture
def local_backend(mock_config):
    """Create a LocalStorageBackend instance for testing."""
    return LocalStorageBackend(config=mock_config)


async def test_vector_document_creation():
    """Test VectorDocument creation."""
    doc = VectorDocument(
        id="test_id",
        embedding=[0.1, 0.2, 0.3],
        text="Test document",
        metadata={"key": "value"},
        checksum="sha256:abc123",
        modified_at=datetime.now(),
    )

    assert doc.id == "test_id"
    assert len(doc.embedding) == 3
    assert doc.text == "Test document"
    assert doc.metadata["key"] == "value"


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_local_backend_get_collections_empty(local_backend):
    """Test getting collections when none exist."""
    collections = await local_backend.get_collections()
    assert isinstance(collections, list)
    assert len(collections) == 0


@pytest.mark.asyncio
async def test_local_backend_collection_exists(local_backend):
    """Test checking if a collection exists."""
    exists = await local_backend.collection_exists("nonexistent_collection")
    assert exists is False


@pytest.mark.asyncio
async def test_local_backend_put_and_get_vectors(local_backend):
    """Test storing and retrieving vectors."""
    collection_name = "test_collection"

    # Create test vectors
    vectors = [
        VectorDocument(
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
            text="First document",
            metadata={"index": 1},
        ),
        VectorDocument(
            id="doc2",
            embedding=[0.4, 0.5, 0.6],
            text="Second document",
            metadata={"index": 2},
        ),
    ]

    # Store vectors
    await local_backend.put_vectors(collection_name, vectors)

    # Verify collection exists
    exists = await local_backend.collection_exists(collection_name)
    assert exists is True

    # Retrieve all vectors
    retrieved = await local_backend.get_vectors(collection_name)
    assert len(retrieved) == 2

    # Check content
    ids = {v.id for v in retrieved}
    assert "doc1" in ids
    assert "doc2" in ids

    # Retrieve specific vector
    specific = await local_backend.get_vectors(collection_name, ids=["doc1"])
    assert len(specific) == 1
    assert specific[0].id == "doc1"
    assert specific[0].text == "First document"


@pytest.mark.asyncio
async def test_local_backend_delete_vectors(local_backend):
    """Test deleting vectors."""
    collection_name = "test_delete_collection"

    # Create and store vectors
    vectors = [
        VectorDocument(
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
            text="First document",
            metadata={},
        ),
        VectorDocument(
            id="doc2",
            embedding=[0.4, 0.5, 0.6],
            text="Second document",
            metadata={},
        ),
    ]
    await local_backend.put_vectors(collection_name, vectors)

    # Delete one vector
    await local_backend.delete_vectors(collection_name, ["doc1"])

    # Verify only doc2 remains
    remaining = await local_backend.get_vectors(collection_name)
    assert len(remaining) == 1
    assert remaining[0].id == "doc2"


@pytest.mark.asyncio
async def test_local_backend_sync_metadata(local_backend):
    """Test sync metadata operations."""
    collection_name = "test_sync_metadata"

    # Initially no sync timestamp
    last_sync = await local_backend.get_last_sync(collection_name)
    assert last_sync is None

    # Set sync timestamp
    now = datetime.now()
    await local_backend.set_last_sync(collection_name, now)

    # Retrieve and verify
    retrieved_sync = await local_backend.get_last_sync(collection_name)
    assert retrieved_sync is not None
    # Compare with some tolerance for serialization
    assert abs((retrieved_sync - now).total_seconds()) < 1


@pytest.mark.asyncio
async def test_local_backend_collection_metadata(local_backend):
    """Test getting collection metadata."""
    collection_name = "test_metadata_collection"

    # Get metadata for non-existent collection
    metadata = await local_backend.get_collection_metadata(collection_name)
    assert metadata == {}

    # Create collection with vectors
    vectors = [
        VectorDocument(
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
            text="Test",
            metadata={},
        )
    ]
    await local_backend.put_vectors(collection_name, vectors)

    # Get metadata
    metadata = await local_backend.get_collection_metadata(collection_name)
    assert "name" in metadata
    assert metadata["name"] == collection_name
    assert "count" in metadata
    assert metadata["count"] == 1


@pytest.mark.asyncio
async def test_checksum_calculation(local_backend):
    """Test that checksums are calculated for vectors."""
    collection_name = "test_checksum"

    vector = VectorDocument(
        id="doc1",
        embedding=[0.1, 0.2, 0.3],
        text="Test document",
        metadata={"key": "value"},
    )

    await local_backend.put_vectors(collection_name, [vector])

    # Retrieve and check checksum
    retrieved = await local_backend.get_vectors(collection_name)
    assert len(retrieved) == 1
    assert retrieved[0].checksum is not None
    assert retrieved[0].checksum.startswith("sha256:")
