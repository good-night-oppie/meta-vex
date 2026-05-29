# F02 — Coach MCP Integration

**Phase:** 1
**Status:** in-progress
**Depends on:** F01

## Goal

`ai-builders-coach` MCP usable from agentdex with hub-cache invariant.
Adopt granular tools (`list_endpoints`, `get_endpoint`, `get_schema`) as
they ship from upstream.

## Deliverables

- [x] `agentdex.coach.CoachCache` — ETag-aware single-fetch
- [x] Test `test_hub_fanout_uses_single_spec` asserts fetch_count == 1
- [ ] Real coach call smoke test (gated behind `META_VEX_LIVE_COACH=1` env)
- [ ] Adopt `list_endpoints` / `get_endpoint` / `get_schema` when upstream ships
- [ ] Capture before/after benchmark; post to `mailbox/all.md` BENCH section
- [ ] Refresh ADR-0004 with granular-tool addendum

## Exit criteria

- 3-leaf swarm completes against live coach with single spec fetch
- No 429 from `space.ai-builders.com` for 5+ consecutive runs
- BENCH artifact lives under `docs/bench/`
