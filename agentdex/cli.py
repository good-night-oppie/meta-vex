"""Top-level CLI — bridges `swarm` (PHASE-1) + `battle` (PHASE-2)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

# Import to populate registries.
import agentdex.modules.agents.trivial  # noqa: F401
import agentdex.modules.tasks.trivial  # noqa: F401
import agentdex.swarm.leaf  # noqa: F401
from agentdex.modules.agents.models import AgentVersion, AutonomyPolicy
from agentdex.modules.agents.trivial import make_agent
from agentdex.modules.battles.engine import BattleSide, run_battle
from agentdex.modules.battles.takers import OrchestratorTurnTaker
from agentdex.modules.tasks.trivial import get_task
from agentdex.shared.helios_adapter import SQLiteCheckpointStore
from agentdex.swarm.cli import main as swarm_main


async def _cmd_battle(args: argparse.Namespace) -> int:
    task = get_task(args.task)

    if args.mode != "autonomous":
        print(
            f"error: only --mode autonomous supported in PHASE-2 MVP "
            f"(got {args.mode!r})",
            file=sys.stderr,
        )
        return 2

    a_runner = make_agent(args.agent_a)
    b_runner = make_agent(args.agent_b)
    a_version = AgentVersion(
        id=f"{args.agent_a}@mvp",
        name=args.agent_a,
        harness_blob=f"<trivial:{args.agent_a}>",
        autonomy_policy=AutonomyPolicy.FULL_AUTO,
    )
    b_version = AgentVersion(
        id=f"{args.agent_b}@mvp",
        name=args.agent_b,
        harness_blob=f"<trivial:{args.agent_b}>",
        autonomy_policy=AutonomyPolicy.FULL_AUTO,
    )
    taker_a = OrchestratorTurnTaker()
    taker_b = OrchestratorTurnTaker()
    store = SQLiteCheckpointStore()

    side_a = BattleSide("a", a_version, a_runner, taker_a)
    side_b = BattleSide("b", b_version, b_runner, taker_b)

    result, tree = await run_battle(task, side_a, side_b, store)
    print(json.dumps({
        "battle_id": result.battle_id,
        "task_id": result.task_id,
        "winner": result.winner.value,
        "side_a": result.side_a.model_dump(),
        "side_b": result.side_b.model_dump(),
        "objectives": result.objectives,
        "tree": {
            "checkpoints": len(tree.checkpoints),
            "branches": len(tree.branches),
        },
    }, indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    # Two top-level domains: 'swarm' (PHASE-1) + 'battle' (PHASE-2).
    # If first arg is 'swarm', delegate to the existing swarm CLI verbatim.
    argv = argv if argv is not None else sys.argv[1:]
    if argv and argv[0] == "swarm":
        return swarm_main(argv)

    parser = argparse.ArgumentParser(prog="agentdex")
    sub = parser.add_subparsers(dest="domain", required=True)
    sub.add_parser("swarm", help="(see `agentdex swarm --help`)").add_argument(
        "_swarm_args", nargs="*"
    )

    battle = sub.add_parser("battle", help="run an agent battle")
    battle.add_argument(
        "agent_a", help="left side agent name (see agentdex/modules/agents/trivial.py)"
    )
    battle.add_argument("agent_b", help="right side agent name")
    battle.add_argument(
        "--task", required=True, help="task id (see agentdex/modules/tasks/trivial.py)"
    )
    battle.add_argument(
        "--mode",
        default="autonomous",
        choices=["autonomous"],
        help="battle mode (MVP supports autonomous only)",
    )

    args = parser.parse_args(argv)
    if args.domain == "battle":
        return asyncio.run(_cmd_battle(args))

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
