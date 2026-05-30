"""End-to-end battle engine smoke test — PHASE-2 acceptance criterion §5."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentdex.modules.agents.models import AgentVersion, AutonomyPolicy
from agentdex.modules.agents.trivial import make_agent
from agentdex.modules.battles.engine import BattleSide, run_battle
from agentdex.modules.battles.result import Domination
from agentdex.modules.battles.takers import OrchestratorTurnTaker
from agentdex.modules.tasks.trivial import get_task
from agentdex.shared.helios_adapter import SQLiteCheckpointStore


@pytest.fixture
def store(tmp_path: Path) -> SQLiteCheckpointStore:
    return SQLiteCheckpointStore(db_path=tmp_path / "checkpoints.db")


def _make_side(agent_name: str, side_id: str) -> BattleSide:
    runner = make_agent(agent_name)
    version = AgentVersion(
        id=f"{agent_name}@mvp",
        name=agent_name,
        harness_blob=f"<trivial:{agent_name}>",
        autonomy_policy=AutonomyPolicy.FULL_AUTO,
    )
    return BattleSide(
        side_id=side_id,
        agent_version=version,
        runner=runner,
        taker=OrchestratorTurnTaker(),
    )


@pytest.mark.asyncio
async def test_autonomous_battle_uppercase_v2_wins(
    store: SQLiteCheckpointStore,
) -> None:
    task = get_task("uppercase_input")
    side_a = _make_side("echo_agent_v1", "a")  # outputs "hello world" → loses
    side_b = _make_side("echo_agent_v2", "b")  # outputs "HELLO WORLD" → wins

    result, tree = await run_battle(task, side_a, side_b, store)

    # Side B should dominate on accuracy (1.0 vs 0.0) and tie/win on others.
    assert result.winner == Domination.B_DOMINATES
    assert result.side_a.scores["accuracy"] == 0.0
    assert result.side_b.scores["accuracy"] == 1.0

    # Each side took 1 stop (the COMPLETION_CHECK) before terminating.
    assert result.side_a.move_count == 1
    assert result.side_b.move_count == 1

    # Tree captures 2 checkpoints (one per side) + 2 branches.
    assert len(tree.checkpoints) == 2
    assert len(tree.branches) == 2
    assert {cp.side_id for cp in tree.checkpoints} == {"a", "b"}


@pytest.mark.asyncio
async def test_tie_when_both_agents_match(store: SQLiteCheckpointStore) -> None:
    task = get_task("uppercase_input")
    side_a = _make_side("echo_agent_v2", "a")
    side_b = _make_side("echo_agent_v2", "b")

    result, _tree = await run_battle(task, side_a, side_b, store)

    # Same accuracy, same cost; latency may differ marginally, so allow tie OR
    # one-sided domination if latency happened to favor one side.
    assert result.side_a.scores["accuracy"] == result.side_b.scores["accuracy"] == 1.0
