#!/usr/bin/env python3
"""3-leaf swarm bench against ai-builders-coach MCP.

Compares two patterns:
  - mode_naive:    each leaf spawns its own MCP child + calls get_api_specification.
                   3,553-line spec round-trips N times through MCP stdio.
  - mode_hubcache: single CoachCache.fetch_spec() at hub; leaves consume cached
                   dict slice in-memory; MCP touched once (or zero with warm disk cache).

Metrics captured per mode:
  - wall_time_s         end-to-end wall clock
  - total_payload_bytes total bytes returned to swarm orchestrator
  - mcp_invocations     count of get_api_specification calls
  - leaf_times_s        per-leaf timing

Usage:
  uv run python scripts/bench_coach_swarm.py [--leaves 3] [--cold] [--out PATH]

`--cold` clears `~/.ai-builders-mcp-cache/openapi_spec_cache.json` before each mode
to compare on a cold MCP-server cache.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from meta_vex.coach import CoachCache  # noqa: E402

MCP_BIN = os.environ.get("MCP_COACH_BIN", str(Path.home() / ".npm-global" / "bin" / "mcp-coach-server"))
MCP_DISK_CACHE = Path.home() / ".ai-builders-mcp-cache"
COACH_BASE_URL = os.environ.get("COACH_BASE_URL", "https://space.ai-builders.com/backend")


@dataclass
class ModeResult:
    mode: str
    leaves: int
    wall_time_s: float
    total_payload_bytes: int
    mcp_invocations: int
    leaf_times_s: list[float]
    cold_disk_cache: bool


def clear_mcp_disk_cache() -> None:
    if MCP_DISK_CACHE.exists():
        shutil.rmtree(MCP_DISK_CACHE)


def clear_hub_cache(cache_dir: Path) -> None:
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


async def call_mcp_get_spec() -> tuple[float, int]:
    """Spawn a fresh MCP child, call get_api_specification, return (elapsed_s, bytes).

    Each call = own process (= what a swarm leaf would do in naive mode).
    """

    def _sync_call() -> tuple[float, int]:
        proc = subprocess.Popen(
            [MCP_BIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        assert proc.stdin and proc.stdout
        try:
            send = lambda m: (proc.stdin.write(json.dumps(m) + "\n"), proc.stdin.flush())  # noqa: E731
            recv = lambda: json.loads(proc.stdout.readline())

            send({
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "bench", "version": "0"},
                },
            })
            recv()
            send({"jsonrpc": "2.0", "method": "notifications/initialized"})

            t0 = time.time()
            send({
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "get_api_specification", "arguments": {}},
            })
            resp = recv()
            dt = time.time() - t0
            content = resp.get("result", {}).get("content", [])
            payload_bytes = sum(len(c.get("text", "").encode()) for c in content)
            return dt, payload_bytes
        finally:
            proc.terminate()
            proc.wait(timeout=2)

    return await asyncio.to_thread(_sync_call)


async def mode_naive(leaves: int) -> ModeResult:
    t0 = time.time()
    results = await asyncio.gather(*(call_mcp_get_spec() for _ in range(leaves)))
    wall = time.time() - t0
    leaf_times = [r[0] for r in results]
    payload = sum(r[1] for r in results)
    return ModeResult(
        mode="naive",
        leaves=leaves,
        wall_time_s=wall,
        total_payload_bytes=payload,
        mcp_invocations=leaves,
        leaf_times_s=leaf_times,
        cold_disk_cache=False,  # filled by caller
    )


async def leaf_reason_on_slice(spec: dict, slice_key: str) -> tuple[float, int]:
    """Trivial leaf workload — receives in-memory spec slice, returns synth result."""
    t0 = time.time()
    sub = spec.get(slice_key) or {}
    # synthetic reasoning: count items, no MCP call
    if isinstance(sub, dict):
        n = sum(len(v) for v in sub.values() if hasattr(v, "__len__"))
    else:
        n = len(sub)
    await asyncio.sleep(0)
    dt = time.time() - t0
    # payload = serialized result size (what the leaf returns to orchestrator)
    return dt, len(json.dumps({"slice": slice_key, "count": n}).encode())


async def mode_hubcache(leaves: int, cache_dir: Path) -> ModeResult:
    cache = CoachCache(base_url=COACH_BASE_URL, cache_dir=cache_dir)
    t0 = time.time()
    spec = await cache.fetch_spec()
    keys = list(spec.keys())
    slice_keys = [keys[i % len(keys)] for i in range(leaves)]
    leaf_results = await asyncio.gather(*(leaf_reason_on_slice(spec, k) for k in slice_keys))
    wall = time.time() - t0
    leaf_times = [r[0] for r in leaf_results]
    payload = sum(r[1] for r in leaf_results)
    return ModeResult(
        mode="hubcache",
        leaves=leaves,
        wall_time_s=wall,
        total_payload_bytes=payload,
        mcp_invocations=0,  # hub-cache uses raw HTTP; MCP not touched
        leaf_times_s=leaf_times,
        cold_disk_cache=False,
    )


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leaves", type=int, default=3)
    ap.add_argument("--cold", action="store_true",
                    help="Clear MCP disk cache + hub cache before each mode")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "docs" / "bench" /
                    f"{time.strftime('%Y-%m-%d')}-coach-1.0.10-{3}leaf.json")
    args = ap.parse_args()

    hub_cache_dir = Path("/tmp/meta-vex-bench")

    print(f"=== bench: {args.leaves} leaves, cold={args.cold} ===")
    print(f"  MCP binary: {MCP_BIN}")
    print(f"  Coach base URL: {COACH_BASE_URL}")
    print(f"  MCP disk cache: {MCP_DISK_CACHE}")
    print(f"  Hub cache:      {hub_cache_dir}")
    print()

    results: list[ModeResult] = []

    for cold in ([True, False] if args.cold else [False]):
        if cold:
            clear_mcp_disk_cache()
            clear_hub_cache(hub_cache_dir)
            print(f"--- COLD pass (caches cleared) ---")
        else:
            print(f"--- WARM pass (caches retained) ---")

        for mode_fn, name in [(mode_naive, "naive"), (mode_hubcache, "hubcache")]:
            if name == "naive":
                r = await mode_naive(args.leaves)
            else:
                r = await mode_hubcache(args.leaves, hub_cache_dir)
            r.cold_disk_cache = cold
            results.append(r)
            print(f"  {name:10s} wall={r.wall_time_s*1000:7.1f}ms  "
                  f"bytes={r.total_payload_bytes:>9,}  "
                  f"mcp_calls={r.mcp_invocations}  "
                  f"leaves={r.leaves}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps([asdict(r) for r in results], indent=2))
    print(f"\nWrote: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
