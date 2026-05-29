# F03 — Swarm Runtime

**Phase:** 1
**Status:** in-progress
**Depends on:** F02

## Goal

Hub-and-leaf primitives generalizable beyond coach — usable for arbitrary
fan-out workloads against ionq runtime.

## Deliverables

- [x] `agentdex.swarm.hub.Hub` with `LeafTask` dataclass + anyio task group
- [x] Reference leaves: `count_endpoints`, `list_schema_names`
- [x] Leaf task registry / discovery (`@register` decorator, CLI `agentdex swarm run`)
- [x] Result aggregation contract (typed `LeafResult` + `FailureMode`)
- [x] Fail-fast vs collect-errors mode toggle (`Hub.run(..., mode=FailureMode.COLLECT)`)
- [ ] Integration with ionq agents (run leaf inside ionq sandbox VFS) — deferred

## Exit criteria

- [x] Define + run a 5-leaf workload that consumes a non-coach data source
      (`tests/test_swarm.py::test_five_leaf_non_coach_workload`)
- [x] Failure of one leaf does not crash hub (collect-errors mode)
      (`tests/test_swarm.py::test_collect_mode_one_failure_does_not_crash_hub`)
- [ ] Round-trip through ionq agent works end-to-end — deferred to F03 follow-up

## CLI surface

```bash
agentdex swarm list                                                  # registered leaves
agentdex swarm run count_records group_by_kind sum_value \
    --dataset path/to/records.json --mode collect                    # generic workload
agentdex swarm run count_endpoints list_schema_names                 # coach workload (uses cache)
```
