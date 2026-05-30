"""SQLiteCheckpointStore round-trip tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdex.shared.helios_adapter import SQLiteCheckpointStore


@pytest.fixture
def store(tmp_path: Path) -> SQLiteCheckpointStore:
    return SQLiteCheckpointStore(db_path=tmp_path / "checkpoints.db")


@pytest.mark.asyncio
async def test_put_get_roundtrip(store: SQLiteCheckpointStore) -> None:
    state = {"side_id": "a", "move_idx": 0, "agent_output": "hello"}
    state_hash = await store.put(state)
    assert state_hash
    restored = await store.get(state_hash)
    assert restored == state


@pytest.mark.asyncio
async def test_put_is_idempotent_for_identical_state(store: SQLiteCheckpointStore) -> None:
    state = {"k": "v"}
    h1 = await store.put(state)
    h2 = await store.put(state)
    assert h1 == h2


@pytest.mark.asyncio
async def test_get_unknown_hash_raises(store: SQLiteCheckpointStore) -> None:
    with pytest.raises(KeyError):
        await store.get("nonexistent")


@pytest.mark.asyncio
async def test_exists(store: SQLiteCheckpointStore) -> None:
    state = {"x": 1}
    h = await store.put(state)
    assert await store.exists(h)
    assert not await store.exists("ffffffffffffffff")
