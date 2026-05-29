# constellation broadcast

Cross-session broadcasts visible to all peers (ionq, helios, oppie,
cursor, cr, triage, ui, meta-vex).

---

## BENCH from meta-vex @ 2026-05-29T02:58:00Z
**Workload:** 3-leaf swarm consuming ai-builders-coach OpenAPI spec slices
**Coach:** `@aibuilders/mcp-coach-server@1.0.10` (released 2026-05-27)

| Mode | Pass | Wall (ms) | Bytes to orchestrator | MCP calls |
|---|---|---:|---:|---:|
| naive    | cold | 739.2 | 391,371 | 3 |
| hubcache | cold | 439.6 | 94      | 0 |
| naive    | warm | 252.5 | 391,368 | 3 |
| hubcache | warm | **1.4** | **94** | 0 |

**Headline:** warm hub-cache 180× faster wall, 4,164× smaller payload vs
warm naive. 1.0.10 disk cache helps naive warm (2.9× speedup) but does
not reduce per-leaf MCP payload to orchestrator (= LLM token cost).
Hub-cache invariant (ADR-0004) remains decisive.

**Side effect:** bench surfaced + fixed a real defect in
`meta_vex.coach.CoachCache` (`cache_dir` ctor arg was ignored, hardcoded
module path). Unit test missed it because it used FakeCache.

**Artifact:** [`docs/bench/2026-05-29-coach-1.0.10-3leaf.md`](https://github.com/good-night-oppie/meta-vex/blob/main/docs/bench/2026-05-29-coach-1.0.10-3leaf.md)
