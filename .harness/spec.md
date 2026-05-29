# Active spec

## Task
Build and dogfood swarm patterns on top of `ai-builders-coach` MCP that
demonstrate the ionq · helios · oppie trio's value without hammering
upstream rate limits or N×-burning tokens. Current focus: PHASE-1
features F01–F04 (see `features/PHASE-1/`).

## Acceptance criteria
1. Hub-cache invariant holds — `Hub.run()` performs exactly one coach
   spec fetch regardless of leaf count (verified by `test_hub_fanout_uses_single_spec`).
2. 3-leaf swarm completes against live coach without triggering 429 from
   `space.ai-builders.com`.
3. Loop driver tick (`scripts/loop_driver.sh`) writes a heartbeat snapshot
   to `~/.cursor/projects/home-etang/heartbeat/snapshots/agentdex.txt`
   reflecting current branch, commit, stage, mailbox depth.

## Out-of-scope (do not touch)
- `.cursor/` and `.claude/` hook source (owned by ionq-hooks upstream;
  patch there, regenerate here)
- `hooks/_ionq_hooks/` (same — upstream-owned)
- Any front-end JS / Next.js surface (deferred to PHASE-2)

## Non-goals
- Wrapping coach MCP with our own RPC layer (defeats hub-cache contract)
- Adding caching at leaf layer (cache is hub-layer invariant, ADR-0004)
- Public deploy infra (PHASE-4)

## Definition of done
- All visible AND held-out tests pass.
- No new `@pytest.mark.skip` / `xfail` / `# noqa` / `# type: ignore` unless disclosed.
- Only files in `.harness/files-allowed` modified.
- LLM judge returns `VERDICT: AGREE`.
- Foundational ADRs (0001–0004) still reflect the change; updated if not.
