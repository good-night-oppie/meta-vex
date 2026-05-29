"""Hub orchestrator: warms coach cache, fans out leaf tasks."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import anyio

from agentdex.coach import CoachCache
from agentdex.swarm.result import FailureMode, LeafResult


@dataclass
class LeafTask:
    name: str
    spec_slice_keys: list[str]
    work: Callable[[dict[str, Any]], Awaitable[Any]]


class Hub:
    """Single coach fetch, parallel leaf dispatch.

    Invariant: coach spec is fetched ONCE before any leaf runs. Leaves never
    call coach MCP directly — they receive a spec slice argument.

    Failure modes:
      - FAIL_FAST (default): first leaf exception aborts the swarm.
      - COLLECT: exceptions captured into LeafResult.error; swarm completes.
    """

    def __init__(self, cache: CoachCache | None = None):
        self.cache = cache or CoachCache()

    async def run(
        self,
        tasks: list[LeafTask],
        *,
        mode: FailureMode = FailureMode.FAIL_FAST,
    ) -> dict[str, LeafResult]:
        spec = await self.cache.fetch_spec()
        return await self.run_with_spec(spec, tasks, mode=mode)

    async def run_with_spec(
        self,
        spec: dict[str, Any],
        tasks: list[LeafTask],
        *,
        mode: FailureMode = FailureMode.FAIL_FAST,
    ) -> dict[str, LeafResult]:
        """Variant for non-coach workloads — caller provides the dataset."""
        results: dict[str, LeafResult] = {}

        async def _run_leaf(task: LeafTask) -> None:
            spec_slice = {k: spec.get(k) for k in task.spec_slice_keys}
            t0 = time.perf_counter()
            try:
                value = await task.work(spec_slice)
                results[task.name] = LeafResult(
                    name=task.name,
                    value=value,
                    error=None,
                    elapsed_s=time.perf_counter() - t0,
                )
            except BaseException as exc:  # noqa: BLE001
                results[task.name] = LeafResult(
                    name=task.name,
                    value=None,
                    error=exc,
                    elapsed_s=time.perf_counter() - t0,
                )
                if mode == FailureMode.FAIL_FAST:
                    raise

        async with anyio.create_task_group() as tg:
            for task in tasks:
                tg.start_soon(_run_leaf, task)

        return results
