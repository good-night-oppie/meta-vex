"""Hub orchestrator: warms coach cache, fans out leaf tasks."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import anyio

from meta_vex.coach import CoachCache


@dataclass
class LeafTask:
    name: str
    spec_slice_keys: list[str]
    work: Callable[[dict[str, Any]], Awaitable[Any]]


class Hub:
    """Single coach fetch, parallel leaf dispatch.

    Invariant: coach spec is fetched ONCE before any leaf runs. Leaves never
    call coach MCP directly — they receive a spec slice argument.
    """

    def __init__(self, cache: CoachCache | None = None):
        self.cache = cache or CoachCache()

    async def run(self, tasks: list[LeafTask]) -> dict[str, Any]:
        spec = await self.cache.fetch_spec()
        results: dict[str, Any] = {}

        async def _run_leaf(task: LeafTask) -> None:
            spec_slice = {k: spec.get(k) for k in task.spec_slice_keys}
            results[task.name] = await task.work(spec_slice)

        async with anyio.create_task_group() as tg:
            for task in tasks:
                tg.start_soon(_run_leaf, task)

        return results
