"""Tests for sync engine."""

import pytest
from datetime import datetime
from corpus_callosum.sync.engine import (
    SyncEngine,
    SyncDirection,
    SyncStrategy,
    SyncDiff,
    SyncResult,
)
from corpus_callosum.storage.base import VectorDocument, StorageBackend


class MockStorageBackend(StorageBackend):
    """Mock storage backend for testing."""

    def __init__(self):
        self.data = {}  # collection_name -> {doc_id -> VectorDocument}
        self.sync_times = {}  # collection_name -> datetime

    async def get_collections(self):
        return list(self.data.keys())

    async def get_collection_metadata(self, collection):
        if collection in self.data:
            return {"name": collection, "count": len(self.data[collection])}
        return {}

    async def get_vectors(self, collection, ids=None):
        if collection not in self.data:
            return []

        if ids is None:
            return list(self.data[collection].values())

        return [self.data[collection][doc_id] for doc_id in ids if doc_id in self.data[collection]]

    async def put_vectors(self, collection, vectors):
        if collection not in self.data:
            self.data[collection] = {}

        for vec in vectors:
            self.data[collection][vec.id] = vec

    async def delete_vectors(self, collection, ids):
        if collection not in self.data:
            return

        for doc_id in ids:
            self.data[collection].pop(doc_id, None)

    async def get_last_sync(self, collection):
        return self.sync_times.get(collection)

    async def set_last_sync(self, collection, timestamp):
        self.sync_times[collection] = timestamp

    async def collection_exists(self, collection):
        return collection in self.data


@pytest.mark.asyncio
async def test_sync_diff_empty():
    """Test diff when both backends are empty."""
    local = MockStorageBackend()
    remote = MockStorageBackend()
    engine = SyncEngine(local, remote)

    diff = await engine.get_diff("test_collection")

    assert diff.collection == "test_collection"
    assert len(diff.local_only) == 0
    assert len(diff.remote_only) == 0
    assert len(diff.conflicts) == 0
    assert len(diff.in_sync) == 0


@pytest.mark.asyncio
async def test_sync_diff_local_only():
    """Test diff with local-only documents."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add document to local only
    await local.put_vectors(
        "test",
        [VectorDocument(id="doc1", embedding=[0.1], text="Test", metadata={}, checksum="sha256:123")],
    )

    engine = SyncEngine(local, remote)
    diff = await engine.get_diff("test")

    assert len(diff.local_only) == 1
    assert "doc1" in diff.local_only
    assert len(diff.remote_only) == 0


@pytest.mark.asyncio
async def test_sync_diff_remote_only():
    """Test diff with remote-only documents."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add document to remote only
    await remote.put_vectors(
        "test",
        [VectorDocument(id="doc2", embedding=[0.2], text="Test", metadata={}, checksum="sha256:456")],
    )

    engine = SyncEngine(local, remote)
    diff = await engine.get_diff("test")

    assert len(diff.local_only) == 0
    assert len(diff.remote_only) == 1
    assert "doc2" in diff.remote_only


@pytest.mark.asyncio
async def test_sync_diff_in_sync():
    """Test diff with documents in sync."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add same document to both
    doc = VectorDocument(id="doc1", embedding=[0.1], text="Test", metadata={}, checksum="sha256:123")
    await local.put_vectors("test", [doc])
    await remote.put_vectors("test", [doc])

    engine = SyncEngine(local, remote)
    diff = await engine.get_diff("test")

    assert len(diff.in_sync) == 1
    assert "doc1" in diff.in_sync
    assert len(diff.conflicts) == 0


@pytest.mark.asyncio
async def test_sync_diff_conflicts():
    """Test diff with conflicting documents."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add different versions to local and remote
    await local.put_vectors(
        "test",
        [VectorDocument(id="doc1", embedding=[0.1], text="Local", metadata={}, checksum="sha256:local")],
    )
    await remote.put_vectors(
        "test",
        [
            VectorDocument(
                id="doc1", embedding=[0.2], text="Remote", metadata={}, checksum="sha256:remote"
            )
        ],
    )

    engine = SyncEngine(local, remote)
    diff = await engine.get_diff("test")

    assert len(diff.conflicts) == 1
    assert "doc1" in diff.conflicts


@pytest.mark.asyncio
async def test_sync_pull():
    """Test pulling from remote to local."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add document to remote
    await remote.put_vectors(
        "test",
        [VectorDocument(id="doc1", embedding=[0.1], text="Remote", metadata={}, checksum="sha256:123")],
    )

    engine = SyncEngine(local, remote)
    result = await engine.sync("test", direction=SyncDirection.PULL)

    assert result.success is True
    assert result.pulled_count == 1

    # Verify document was pulled to local
    local_docs = await local.get_vectors("test")
    assert len(local_docs) == 1
    assert local_docs[0].id == "doc1"


@pytest.mark.asyncio
async def test_sync_push():
    """Test pushing from local to remote."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add document to local
    await local.put_vectors(
        "test",
        [VectorDocument(id="doc1", embedding=[0.1], text="Local", metadata={}, checksum="sha256:123")],
    )

    engine = SyncEngine(local, remote)
    result = await engine.sync("test", direction=SyncDirection.PUSH)

    assert result.success is True
    assert result.pushed_count == 1

    # Verify document was pushed to remote
    remote_docs = await remote.get_vectors("test")
    assert len(remote_docs) == 1
    assert remote_docs[0].id == "doc1"


@pytest.mark.asyncio
async def test_sync_bidirectional():
    """Test bidirectional sync."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add different documents to each
    await local.put_vectors(
        "test",
        [VectorDocument(id="doc1", embedding=[0.1], text="Local", metadata={}, checksum="sha256:123")],
    )
    await remote.put_vectors(
        "test",
        [VectorDocument(id="doc2", embedding=[0.2], text="Remote", metadata={}, checksum="sha256:456")],
    )

    engine = SyncEngine(local, remote)
    result = await engine.sync("test", direction=SyncDirection.BIDIRECTIONAL)

    assert result.success is True
    assert result.pulled_count == 1
    assert result.pushed_count == 1

    # Verify both backends have both documents
    local_docs = await local.get_vectors("test")
    remote_docs = await remote.get_vectors("test")

    assert len(local_docs) == 2
    assert len(remote_docs) == 2


@pytest.mark.asyncio
async def test_sync_all():
    """Test syncing all collections."""
    local = MockStorageBackend()
    remote = MockStorageBackend()

    # Add documents to different collections
    await local.put_vectors(
        "col1",
        [VectorDocument(id="doc1", embedding=[0.1], text="Test", metadata={}, checksum="sha256:123")],
    )
    await remote.put_vectors(
        "col2",
        [VectorDocument(id="doc2", embedding=[0.2], text="Test", metadata={}, checksum="sha256:456")],
    )

    engine = SyncEngine(local, remote)
    results = await engine.sync_all(direction=SyncDirection.BIDIRECTIONAL)

    assert len(results) == 2
    assert "col1" in results
    assert "col2" in results
    assert results["col1"].success is True
    assert results["col2"].success is True


def test_sync_result_duration():
    """Test sync result duration calculation."""
    result = SyncResult(
        collection="test",
        success=True,
        direction=SyncDirection.PULL,
        start_time=datetime(2026, 1, 1, 12, 0, 0),
        end_time=datetime(2026, 1, 1, 12, 0, 5),
    )

    duration = result.duration_seconds
    assert duration == 5.0
