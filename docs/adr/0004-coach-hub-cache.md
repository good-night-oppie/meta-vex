# ADR-0004: Hub-cache pattern for ai-builders-coach MCP

**Date:** 2026-05-28
**Status:** Accepted

## Context

`ai-builders-coach` `get_api_specification` returns 3,553+ lines of OpenAPI
spec. In swarm mode (3+ leaves), naive fan-out:

1. MCP stdio is single-pipe JSON-RPC → calls serialize at transport
2. Each leaf re-downloads → N × token cost, blows Claude tool-result max
   token cap (auto-spill to `tool-results/*.txt`)
3. Upstream `space.ai-builders.com` rate-limits at low N (429s observed)

Author (`@鸭哥`) is shipping granular tools (`list_endpoints`,
`get_endpoint`, `get_schema`) — pattern below remains correct even after
that lands, because hub-cache also handles other large coach outputs.

## Decision

Hub-and-leaf with single-fetch cache:

```
hub:
  CoachCache.fetch_spec() → /tmp/meta-vex/coach-spec.json (+ ETag)
leaves (N parallel):
  Read /tmp/meta-vex/coach-spec.json offset=X limit=Y
  reason on slice
```

`meta_vex.swarm.hub.Hub` enforces the invariant: spec fetched ONCE before
any leaf runs. Leaves receive a `spec_slice` argument, never call coach
MCP directly.

Test `test_hub_fanout_uses_single_spec` asserts the invariant
(`fetch_count == 1` across N leaves).

## Consequences

- Throughput now bounded by leaf compute, not coach IO
- ETag/version layer means re-runs are free when spec unchanged
- When 鸭哥 ships granular tools, leaves can adopt them directly without
  changing the hub-cache contract (cache becomes optional optimization)
