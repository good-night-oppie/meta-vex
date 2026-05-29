"""Built-in leaf workers — registered via `@register`.

Leaves never call coach MCP directly. They receive a `spec_slice` dict
and return a small result. The slice can come from CoachCache (coach
workloads) or any other in-memory dataset (generic workloads).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from agentdex.swarm.registry import register

# --- coach workloads ---


@register("count_endpoints")
async def count_endpoints(spec_slice: dict[str, Any]) -> int:
    paths = spec_slice.get("paths") or {}
    return sum(len(ops) for ops in paths.values() if isinstance(ops, dict))


@register("list_schema_names")
async def list_schema_names(spec_slice: dict[str, Any]) -> list[str]:
    components = spec_slice.get("components") or {}
    schemas = components.get("schemas") or {}
    return sorted(schemas.keys())


# --- generic record-set workloads (non-coach) ---


def _records(spec_slice: dict[str, Any]) -> list[dict[str, Any]]:
    recs = spec_slice.get("records") or []
    return [r for r in recs if isinstance(r, dict)]


@register("count_records")
async def count_records(spec_slice: dict[str, Any]) -> int:
    return len(_records(spec_slice))


@register("group_by_kind")
async def group_by_kind(spec_slice: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in _records(spec_slice):
        k = str(r.get("kind", "?"))
        out[k] = out.get(k, 0) + 1
    return out


@register("unique_ids")
async def unique_ids(spec_slice: dict[str, Any]) -> list[str]:
    seen: set[str] = {str(r["id"]) for r in _records(spec_slice) if "id" in r}
    return sorted(seen)


@register("sum_value")
async def sum_value(spec_slice: dict[str, Any]) -> float:
    vals: Iterable[float] = (float(r.get("value", 0)) for r in _records(spec_slice))
    return sum(vals)


@register("max_value")
async def max_value(spec_slice: dict[str, Any]) -> float:
    vals = [float(r.get("value", 0)) for r in _records(spec_slice)]
    return max(vals) if vals else 0.0


# --- demo failure leaf (for FailureMode.COLLECT testing) ---


@register("always_fail")
async def always_fail(spec_slice: dict[str, Any]) -> None:
    raise RuntimeError("intentional leaf failure for swarm collect-errors test")
