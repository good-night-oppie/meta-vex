"""F03 swarm runtime tests — 5-leaf non-coach workload + failure-mode contract."""

from __future__ import annotations

import pytest

# Importing leaf populates the registry.
import agentdex.swarm.leaf  # noqa: F401
from agentdex.swarm.hub import Hub, LeafTask
from agentdex.swarm.registry import list_names, resolve
from agentdex.swarm.result import FailureMode

SAMPLE_DATASET = {
    "records": [
        {"id": "a", "kind": "x", "value": 1.5},
        {"id": "b", "kind": "x", "value": 2.5},
        {"id": "c", "kind": "y", "value": 4.0},
        {"id": "d", "kind": "y", "value": 7.5},
        {"id": "e", "kind": "z", "value": 0.0},
    ],
}


def _leaves_for(*names: str) -> list[LeafTask]:
    return [LeafTask(name=n, spec_slice_keys=["records"], work=resolve(n)) for n in names]


def test_registry_lists_built_in_leaves() -> None:
    expected = {
        "count_endpoints",
        "list_schema_names",
        "count_records",
        "group_by_kind",
        "unique_ids",
        "sum_value",
        "max_value",
        "always_fail",
    }
    assert expected.issubset(set(list_names()))


def test_registry_resolve_unknown_raises() -> None:
    with pytest.raises(KeyError):
        resolve("not_a_leaf_name")


@pytest.mark.asyncio
async def test_five_leaf_non_coach_workload() -> None:
    hub = Hub()
    tasks = _leaves_for(
        "count_records", "group_by_kind", "unique_ids", "sum_value", "max_value"
    )
    results = await hub.run_with_spec(SAMPLE_DATASET, tasks)

    assert all(r.ok for r in results.values()), {n: r.error for n, r in results.items()}
    assert results["count_records"].value == 5
    assert results["group_by_kind"].value == {"x": 2, "y": 2, "z": 1}
    assert results["unique_ids"].value == ["a", "b", "c", "d", "e"]
    assert results["sum_value"].value == 15.5
    assert results["max_value"].value == 7.5
    for r in results.values():
        assert r.elapsed_s >= 0


@pytest.mark.asyncio
async def test_collect_mode_one_failure_does_not_crash_hub() -> None:
    hub = Hub()
    tasks = _leaves_for("count_records", "always_fail", "sum_value")
    results = await hub.run_with_spec(
        SAMPLE_DATASET, tasks, mode=FailureMode.COLLECT
    )

    assert results["count_records"].ok and results["count_records"].value == 5
    assert results["sum_value"].ok and results["sum_value"].value == 15.5

    failed = results["always_fail"]
    assert not failed.ok
    assert isinstance(failed.error, RuntimeError)
    assert "intentional leaf failure" in str(failed.error)


@pytest.mark.asyncio
async def test_fail_fast_mode_propagates_first_exception() -> None:
    hub = Hub()
    tasks = _leaves_for("always_fail", "count_records")
    with pytest.raises(BaseExceptionGroup) as excinfo:
        await hub.run_with_spec(SAMPLE_DATASET, tasks, mode=FailureMode.FAIL_FAST)
    # anyio wraps task-group exceptions in an ExceptionGroup
    inner = [e for e in excinfo.value.exceptions if isinstance(e, RuntimeError)]
    assert inner, f"expected RuntimeError in group, got {excinfo.value.exceptions!r}"
    assert "intentional leaf failure" in str(inner[0])
