"""Typed result + failure-mode contract for leaf tasks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class FailureMode(StrEnum):
    """How `Hub.run` reacts to a leaf raising.

    - FAIL_FAST: first leaf exception aborts the swarm (re-raised from `Hub.run`).
    - COLLECT:   exceptions are captured into the corresponding `LeafResult.error`;
                 the swarm completes; the caller inspects `result.ok` per leaf.
    """

    FAIL_FAST = "fail_fast"
    COLLECT = "collect"


@dataclass
class LeafResult:
    name: str
    value: Any
    error: BaseException | None
    elapsed_s: float

    @property
    def ok(self) -> bool:
        return self.error is None
