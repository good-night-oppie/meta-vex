"""Agent domain models — Agent identity, versions, lineage."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AutonomyPolicy(StrEnum):
    """How aggressive an agent is about pausing for human input.

    See ADR-0005 §Per-stop UX.
    """

    LENIENT = "lenient"          # proposer handles most stops, human only high-risk
    CAUTIOUS = "cautious"        # human handles most, proposer only trivial
    FULL_AUTO = "full_auto"      # proposer always (cron /loop pattern)
    FULL_MANUAL = "full_manual"  # human always


class AgentVersion(BaseModel):
    """One snapshot of an agent's harness + config.

    Bridges to ionq.HarnessCandidate via shared.ionq_adapter (PHASE-3).
    For MVP, harness_blob is just the agent runner's source string.
    """

    id: str
    name: str
    parent_id: str | None = Field(
        default=None, description="Previous version this evolved from."
    )
    harness_blob: str = Field(
        description="Agent source (Python module text OR config JSON for declarative agents)."
    )
    autonomy_policy: AutonomyPolicy = AutonomyPolicy.FULL_AUTO
    metadata: dict = Field(default_factory=dict)
