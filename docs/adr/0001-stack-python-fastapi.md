# ADR-0001: Stack — Python + uv + FastAPI

**Date:** 2026-05-28
**Status:** Accepted

## Context

meta-vex is the playground / dogfood lane for the `ionq · helios · oppie` trio.
It needs to:
- Drive `ai-builders-coach` MCP swarm workloads
- Sit naturally alongside sibling repos
- Be cheap to iterate solo

## Decision

Python (3.11+) managed with `uv`. HTTP surface via FastAPI + uvicorn.

## Considered alternatives

| Stack | Why not |
|---|---|
| TypeScript + Next.js | Matches `space.ai-builders.com` but no peer in trio uses TS as primary; would diverge tooling |
| Python + Flask | uv ecosystem favors FastAPI; async-first matters for swarm fan-out |
| Hybrid TS-front + Py-back | Premature for solo iteration; two ecosystems = double maintenance |

## Consequences

- Native parity with `ionq` (Python sibling)
- `anyio` task groups for swarm fan-out
- Heavier client-side UI work later if VEX surface grows interactive
