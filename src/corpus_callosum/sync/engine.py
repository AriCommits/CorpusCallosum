"""Synchronization engine for managing data sync between backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..storage.base import StorageBackend, VectorDocument


class SyncDirection(Enum):
    """Direction of synchronization."""

    PULL = "pull"  # Remote -> Local
    PUSH = "push"  # Local -> Remote
    BIDIRECTIONAL = "bidirectional"  # Both directions


class SyncStrategy(Enum):
    """Conflict resolution strategy."""

    LAST_WRITE_WINS = "last_write_wins"
    MANUAL_RESOLVE = "manual_resolve"
    KEEP_BOTH = "keep_both"


@dataclass
class SyncDiff:
    """Differences between local and remote collections."""

    collection: str
    local_only: list[str] = field(default_factory=list)  # IDs only in local
    remote_only: list[str] = field(default_factory=list)  # IDs only in remote
    conflicts: list[str] = field(default_factory=list)  # IDs with different checksums
    in_sync: list[str] = field(default_factory=list)  # IDs with same checksums


@dataclass
class SyncResult:
    """Result of a synchronization operation."""

    collection: str
    success: bool
    direction: SyncDirection
    pulled_count: int = 0
    pushed_count: int = 0
    deleted_count: int = 0
    conflict_count: int = 0
    errors: list[str] = field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Calculate duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class SyncEngine:
    """Engine for synchronizing collections between storage backends."""

    def __init__(self, local: StorageBackend, remote: StorageBackend) -> None:
        """Initialize sync engine.

        Args:
            local: Local storage backend
            remote: Remote storage backend
        """
        self.local = local
        self.remote = remote

    async def sync(
        self,
        collection: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        strategy: SyncStrategy = SyncStrategy.LAST_WRITE_WINS,
        force: bool = False,
    ) -> SyncResult:
        """Synchronize a collection between local and remote storage.

        Args:
            collection: Collection name to sync
            direction: Sync direction (pull, push, or bidirectional)
            strategy: Conflict resolution strategy
            force: Force sync even if conflicts exist

        Returns:
            SyncResult with statistics and status
        """
        result = SyncResult(
            collection=collection,
            success=False,
            direction=direction,
            start_time=datetime.now(),
        )

        try:
            # Get diff between local and remote
            diff = await self.get_diff(collection)

            # Handle based on direction
            if direction == SyncDirection.PULL or direction == SyncDirection.BIDIRECTIONAL:
                await self._pull(collection, diff, strategy, force, result)

            if direction == SyncDirection.PUSH or direction == SyncDirection.BIDIRECTIONAL:
                await self._push(collection, diff, strategy, force, result)

            # Update last sync timestamp
            now = datetime.now()
            await self.local.set_last_sync(collection, now)
            if direction in (SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL):
                await self.remote.set_last_sync(collection, now)

            result.success = True
            result.conflict_count = len(diff.conflicts)

        except Exception as e:
            result.errors.append(str(e))

        result.end_time = datetime.now()
        return result

    async def sync_all(self, **kwargs) -> dict[str, SyncResult]:
        """Sync all collections.

        Args:
            **kwargs: Arguments to pass to sync() for each collection

        Returns:
            Dict mapping collection names to SyncResults
        """
        # Get all collections from both backends
        local_collections = set(await self.local.get_collections())
        remote_collections = set(await self.remote.get_collections())
        all_collections = local_collections | remote_collections

        results: dict[str, SyncResult] = {}
        for collection in all_collections:
            results[collection] = await self.sync(collection, **kwargs)

        return results

    async def get_diff(self, collection: str) -> SyncDiff:
        """Get differences between local and remote.

        Args:
            collection: Collection name

        Returns:
            SyncDiff with differences
        """
        diff = SyncDiff(collection=collection)

        # Get all vectors from both backends
        local_vectors = {v.id: v for v in await self.local.get_vectors(collection)}
        remote_vectors = {v.id: v for v in await self.remote.get_vectors(collection)}

        local_ids = set(local_vectors.keys())
        remote_ids = set(remote_vectors.keys())

        # Find local-only, remote-only, and common IDs
        diff.local_only = list(local_ids - remote_ids)
        diff.remote_only = list(remote_ids - local_ids)
        common_ids = local_ids & remote_ids

        # Check for conflicts in common IDs
        for doc_id in common_ids:
            local_vec = local_vectors[doc_id]
            remote_vec = remote_vectors[doc_id]

            if local_vec.checksum != remote_vec.checksum:
                diff.conflicts.append(doc_id)
            else:
                diff.in_sync.append(doc_id)

        return diff

    async def _pull(
        self,
        collection: str,
        diff: SyncDiff,
        strategy: SyncStrategy,
        force: bool,
        result: SyncResult,
    ) -> None:
        """Pull changes from remote to local.

        Args:
            collection: Collection name
            diff: Sync diff
            strategy: Conflict resolution strategy
            force: Force sync even if conflicts exist
            result: SyncResult to update
        """
        # Pull remote-only documents
        if diff.remote_only:
            remote_docs = await self.remote.get_vectors(collection, ids=diff.remote_only)
            await self.local.put_vectors(collection, remote_docs)
            result.pulled_count += len(remote_docs)

        # Handle conflicts
        if diff.conflicts:
            if strategy == SyncStrategy.LAST_WRITE_WINS:
                await self._resolve_conflicts_last_write_wins(
                    collection, diff.conflicts, from_remote=True, result=result
                )
            elif strategy == SyncStrategy.KEEP_BOTH:
                # For keep_both, we need to rename conflicting documents
                # For now, just use last_write_wins as a fallback
                await self._resolve_conflicts_last_write_wins(
                    collection, diff.conflicts, from_remote=True, result=result
                )
            elif strategy == SyncStrategy.MANUAL_RESOLVE:
                if not force:
                    result.errors.append(
                        f"Conflicts detected: {len(diff.conflicts)} documents. Use --force to resolve."
                    )
                    return

    async def _push(
        self,
        collection: str,
        diff: SyncDiff,
        strategy: SyncStrategy,
        force: bool,
        result: SyncResult,
    ) -> None:
        """Push changes from local to remote.

        Args:
            collection: Collection name
            diff: Sync diff
            strategy: Conflict resolution strategy
            force: Force sync even if conflicts exist
            result: SyncResult to update
        """
        # Push local-only documents
        if diff.local_only:
            local_docs = await self.local.get_vectors(collection, ids=diff.local_only)
            await self.remote.put_vectors(collection, local_docs)
            result.pushed_count += len(local_docs)

        # Handle conflicts
        if diff.conflicts:
            if strategy == SyncStrategy.LAST_WRITE_WINS:
                await self._resolve_conflicts_last_write_wins(
                    collection, diff.conflicts, from_remote=False, result=result
                )
            elif strategy == SyncStrategy.KEEP_BOTH:
                # For keep_both, we need to rename conflicting documents
                # For now, just use last_write_wins as a fallback
                await self._resolve_conflicts_last_write_wins(
                    collection, diff.conflicts, from_remote=False, result=result
                )
            elif strategy == SyncStrategy.MANUAL_RESOLVE:
                if not force:
                    result.errors.append(
                        f"Conflicts detected: {len(diff.conflicts)} documents. Use --force to resolve."
                    )
                    return

    async def _resolve_conflicts_last_write_wins(
        self,
        collection: str,
        conflict_ids: list[str],
        from_remote: bool,
        result: SyncResult,
    ) -> None:
        """Resolve conflicts using last-write-wins strategy.

        Args:
            collection: Collection name
            conflict_ids: List of conflicting document IDs
            from_remote: If True, prefer remote version; otherwise prefer local
            result: SyncResult to update
        """
        if from_remote:
            # Get remote versions and update local
            remote_docs = await self.remote.get_vectors(collection, ids=conflict_ids)
            local_docs_map = {
                v.id: v for v in await self.local.get_vectors(collection, ids=conflict_ids)
            }

            to_update: list[VectorDocument] = []
            for remote_doc in remote_docs:
                local_doc = local_docs_map.get(remote_doc.id)
                if local_doc:
                    # Compare timestamps if available
                    if remote_doc.modified_at and local_doc.modified_at:
                        if remote_doc.modified_at > local_doc.modified_at:
                            to_update.append(remote_doc)
                    else:
                        # No timestamp, just use remote
                        to_update.append(remote_doc)

            if to_update:
                await self.local.put_vectors(collection, to_update)
                result.pulled_count += len(to_update)
        else:
            # Get local versions and update remote
            local_docs = await self.local.get_vectors(collection, ids=conflict_ids)
            remote_docs_map = {
                v.id: v for v in await self.remote.get_vectors(collection, ids=conflict_ids)
            }

            to_update: list[VectorDocument] = []
            for local_doc in local_docs:
                remote_doc = remote_docs_map.get(local_doc.id)
                if remote_doc:
                    # Compare timestamps if available
                    if local_doc.modified_at and remote_doc.modified_at:
                        if local_doc.modified_at > remote_doc.modified_at:
                            to_update.append(local_doc)
                    else:
                        # No timestamp, just use local
                        to_update.append(local_doc)

            if to_update:
                await self.remote.put_vectors(collection, to_update)
                result.pushed_count += len(to_update)
