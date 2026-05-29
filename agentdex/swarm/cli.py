"""CLI entrypoint for swarm operations.

Usage:
    agentdex swarm list
    agentdex swarm run count_records group_by_kind sum_value \
        --dataset path/to/records.json
    agentdex swarm run count_endpoints list_schema_names    # uses coach cache

Examples:
    agentdex swarm run count_records --dataset tests/data/records.json \
        --mode collect
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Import leaf module to populate the registry as a side effect.
import agentdex.swarm.leaf  # noqa: F401
from agentdex.coach import CoachCache
from agentdex.swarm.hub import Hub, LeafTask
from agentdex.swarm.registry import list_names, resolve
from agentdex.swarm.result import FailureMode


def _serialize_result_value(value: object) -> object:
    if isinstance(value, set):
        return sorted(value)
    return value


async def _cmd_list(_args: argparse.Namespace) -> int:
    for name in list_names():
        print(name)
    return 0


async def _cmd_run(args: argparse.Namespace) -> int:
    tasks: list[LeafTask] = [
        LeafTask(name=n, spec_slice_keys=list(args.spec_keys), work=resolve(n))
        for n in args.leaves
    ]
    mode = FailureMode(args.mode)
    hub = Hub(cache=CoachCache())
    if args.dataset:
        spec = json.loads(Path(args.dataset).read_text())
        results = await hub.run_with_spec(spec, tasks, mode=mode)
    else:
        results = await hub.run(tasks, mode=mode)

    summary = {
        name: {
            "ok": r.ok,
            "value": _serialize_result_value(r.value),
            "error": repr(r.error) if r.error else None,
            "elapsed_s": round(r.elapsed_s, 6),
        }
        for name, r in results.items()
    }
    print(json.dumps(summary, indent=2))
    failed = [n for n, r in results.items() if not r.ok]
    return 0 if not failed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agentdex")
    sub = parser.add_subparsers(dest="domain", required=True)

    swarm = sub.add_parser("swarm", help="swarm hub-and-leaf operations")
    swarm_sub = swarm.add_subparsers(dest="action", required=True)

    swarm_sub.add_parser("list", help="list registered leaves")

    run_p = swarm_sub.add_parser("run", help="run a swarm workload")
    run_p.add_argument("leaves", nargs="+", help="leaf names (see `swarm list`)")
    run_p.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="JSON file with the dataset to fan out (skips coach cache)",
    )
    run_p.add_argument(
        "--spec-keys",
        nargs="+",
        default=["paths", "components", "records"],
        help="top-level keys each leaf receives as its slice",
    )
    run_p.add_argument(
        "--mode",
        choices=[m.value for m in FailureMode],
        default=FailureMode.FAIL_FAST.value,
        help="swarm failure mode (default: fail_fast)",
    )

    args = parser.parse_args(argv)

    if args.domain == "swarm":
        if args.action == "list":
            return asyncio.run(_cmd_list(args))
        if args.action == "run":
            return asyncio.run(_cmd_run(args))

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
