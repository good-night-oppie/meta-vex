# F03 — Swarm Runtime

**Phase:** 1
**Status:** in-progress
**Depends on:** F02

## Goal

Hub-and-leaf primitives generalizable beyond coach — usable for arbitrary
fan-out workloads against ionq runtime.

## Deliverables

- [x] `meta_vex.swarm.hub.Hub` with `LeafTask` dataclass + anyio task group
- [x] Reference leaves: `count_endpoints`, `list_schema_names`
- [ ] Leaf task registry / discovery (CLI: `meta-vex swarm run <leaf>`)
- [ ] Result aggregation contract (typed `LeafResult`)
- [ ] Fail-fast vs collect-errors mode toggle
- [ ] Integration with ionq agents (run leaf inside ionq sandbox VFS)

## Exit criteria

- Define + run a 5-leaf workload that consumes a non-coach data source
- Failure of one leaf does not crash hub (collect-errors mode)
- Round-trip through ionq agent works end-to-end
