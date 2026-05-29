"""Leaf registry — decorator-based discovery.

Use `@register("name")` to expose a leaf to the CLI and to swarm
construction by name. The registry is a plain dict; tests can flush it
between cases via `LEAVES.clear()`.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

LeafFn = Callable[[dict[str, Any]], Awaitable[Any]]
LEAVES: dict[str, LeafFn] = {}


def register(name: str) -> Callable[[LeafFn], LeafFn]:
    def deco(fn: LeafFn) -> LeafFn:
        if name in LEAVES:
            raise ValueError(f"leaf {name!r} already registered")
        LEAVES[name] = fn
        return fn

    return deco


def resolve(name: str) -> LeafFn:
    try:
        return LEAVES[name]
    except KeyError as e:
        raise KeyError(f"no leaf registered as {name!r} (known: {sorted(LEAVES)})") from e


def list_names() -> list[str]:
    return sorted(LEAVES)
