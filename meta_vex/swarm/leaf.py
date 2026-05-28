"""Leaf worker primitives — operate on spec slice, never call coach directly."""

from __future__ import annotations

from typing import Any


async def count_endpoints(spec_slice: dict[str, Any]) -> int:
    """Trivial leaf: count operation entries in a paths slice."""
    paths = spec_slice.get("paths") or {}
    return sum(len(ops) for ops in paths.values() if isinstance(ops, dict))


async def list_schema_names(spec_slice: dict[str, Any]) -> list[str]:
    """Trivial leaf: enumerate component schema names."""
    components = spec_slice.get("components") or {}
    schemas = components.get("schemas") or {}
    return sorted(schemas.keys())
