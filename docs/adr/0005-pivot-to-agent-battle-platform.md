# ADR-0005: Pivot to Agent Battle Platform (Agentdex)

**Date:** 2026-05-30
**Status:** Accepted
**Supersedes (in framing):** ADR-0001..0004 (kept for historical foundation; not invalidated)

## Context

The repo started under the name `meta-vex` as a "VEX playground / dogfood lane"
focused on hub-cache patterns for `ai-builders-coach` MCP and parallel swarm
runtime. ADRs 0001-0004 captured that framing — Python stack, ionq-hooks
adoption, swimlane membership, coach hub-cache.

During the 2026-05-29 design session, three successive reframes sharpened the
real product:

1. *"MetaHarness search visualization"* — too narrow; viz isn't a product
2. *"Generic agent evolution platform"* — too abstract; no UX differentiation
3. **"Pokémon Showdown for AI agents"** — locked.

Three orthogonal clarifications fell into place:

- **`ai-builders-coach` MCP is a build-time dev tool**, not a product-layer
  data source. It helps Claude (the developer) write deploy code targeting
  `ai-builders.space`. Hub-cache (ADR-0004) is still correct, but as a
  parallel-coding-agent optimization — not a product feature of Agentdex.
- **`ionq.metaharness` evolves *harnesses*** (single Python files with
  `run(problem)`), not *agents* (multi-component: prompt + tools + memory +
  planning + sub-agents). Agentdex's value-add is the bridge layer: richer
  candidate model, service-style evaluator, per-stop turn-taker, trajectory
  tree.
- **The real differentiator is `parallel turn-based with stop-driven
  checkpoints + trajectory tree forks`** — not Pareto eval, not Elo, not
  evolution. That mechanic is what makes battles legible to humans and what
  earns the helios-CAS investment (Vector A in `HANDOFF_FROM_IONQ.md`).

Domain `agentdex.builders` was registered on Namecheap (1yr + Premium DNS,
2026-05-29). Primary deploy URL is `agentdex.ai-builders.space` (platform
subdomain, no CNAME needed); custom domain parked for future.

## Decision

Agentdex is an **agent battle platform** with the following core mechanics
(all locked by the user on 2026-05-29):

| Mechanic | Choice |
|---|---|
| Battle protocol | Turn-based, two agents run as parallel async tracks |
| Move boundary | Agent's own `StopSignal` (approval / clarification / direction / completion-check) |
| Turn taker | Pluggable per-stop: `HumanTurnTaker` OR `OrchestratorTurnTaker` (LLM proposer) |
| Tree shape | **Trajectory tree** rooted at task init; fork allowed from any checkpoint |
| Win condition | **Pareto domination** across {accuracy, cost, speed} |
| Evolution | **Pareto-driven** — MetaHarness mutation kept iff new candidate dominates incumbent |
| Task source | **Real task the human is working on**, initiated via MCP or CLI (not corpus draws) |
| Visual MVP | **Plain text** (tail-f / HTML two-pre / JSON stream); pretty UI deferred |
| Hosting | `agentdex.ai-builders.space` (platform subdomain) |
| Pricing | GitHub-like freemium: public agents free, private agents paid |
| Social | Twitter-shareable replays (deferred to PHASE-4) |

## Architecture (new module layout)

```
agentdex/
├── modules/
│   ├── agents/       # Agent identity + versions + lineage (wraps ionq HarnessCandidate)
│   ├── tasks/        # TaskContext + scorer registry
│   ├── battles/
│   │   ├── tree.py        # TrajectoryTree, Checkpoint, Branch
│   │   ├── stops.py       # StopSignal, StopReason
│   │   ├── takers.py      # HumanTurnTaker, OrchestratorTurnTaker
│   │   ├── engine.py      # run_battle(side_a, side_b, takers)
│   │   └── replay.py      # load any checkpoint, step forward
│   ├── arena/        # (stub) ladder + per-objective Elo
│   ├── evolver/      # (stub) wraps ionq.MetaHarnessSearch + Pareto check
│   ├── sota/         # (later) external adapters (OpenAI, Anthropic, etc.)
│   ├── billing/      # (later) free vs paid gating
│   └── social/       # (later) OG cards + Twitter share
├── shared/
│   ├── protocols.py       # AgentRunner, Scorer, Mutator
│   ├── helios_adapter.py  # checkpoint storage (helios CAS OR SQLite blob fallback)
│   └── ionq_adapter.py    # HarnessCandidate ↔ AgentVersion bridge
├── swarm/   # KEEP — parallel-branch executor for trajectory tree
├── coach.py # KEEP — build-time deploy helper, not product runtime
└── main.py  # FastAPI app entry
```

## Trio role (unchanged but sharpened)

| Repo | Role | Agentdex consumes via |
|---|---|---|
| `ionq` | MetaHarness proposer + HarnessCandidate + Pareto code | `shared/ionq_adapter.py` |
| `helios` | CAS substrate (O(1) checkpoint snap/restore) | `shared/helios_adapter.py` (with SQLite fallback) |
| `oppie` | trio meta layer | (no direct dep) |
| `ai-builders.space` | hosting platform | deploy via coach MCP at build time |

## Consequences

### Positive

- **Sharper differentiation.** Not "yet another agent eval"; it's gamified PvP
  with a viral replay loop (Pokémon Showdown's growth pattern: ~70% UA from
  shared replays).
- **Trajectory tree earns helios CAS investment.** Vector A in
  `HANDOFF_FROM_IONQ.md` (Merkle CAS + O(1) checkpoint swap) maps directly to
  per-stop forks — without trajectory trees the CAS work would have been
  hard to justify.
- **Real-task init kills the synthetic-benchmark curation burden.** Agentdex
  doesn't need to maintain SWE-bench / HumanEval ports as a primary content
  pipeline; the human's current work IS the content.
- **Per-stop human/proposer toggle matches how users already work today**
  (Claude Code's approval gates, cron `/loop` autonomy). No new mental model.
- **The earlier swarm runtime is repurposable, not wasted** — it becomes the
  parallel-branch executor for trajectory trees.

### Negative

- **Significant rescope.** PHASE-1 features F02-F04 were written for the
  swarm-dogfood framing; they remain valid as foundation but no longer
  describe the product.
- **ADRs 0001-0004 are now "supporting infra", not "product"** — kept as
  historical record. Future readers should start from this ADR.
- **Wider surface area.** Six new modules to build (`battles/`, `evolver/`,
  `arena/`, `social/`, `sota/`, `billing/`) vs the original three.
- **Multi-stakeholder dependencies tighten** — ionq MetaHarness pace,
  helios CAS landing, coach MCP granular-tools roadmap all matter more now.
- **Pricing / billing surface is new** (freemium + private agents quota).
  PHASE-5 work but architecture must not paint us into a corner.
- **Visual / frontend scope is real eventually** even if deferred — the
  battle UX is the differentiator, and a CLI-only product won't capture the
  viral loop.

## Considered alternatives

| Alternative | Why rejected |
|---|---|
| MetaHarness search visualization only | Too narrow; viz is a feature, not a product. Only useful to existing ionq users. |
| Generic agent evolver platform | Too abstract; no UX hook; loses to Inspect / Promptfoo / OpenAI Evals on rigor |
| `Crucible` (tournament without trajectory tree) | Loses the differentiating mechanic — per-stop forks + helios-CAS investment unjustified |
| SaaS-only (no real-task MCP init) | Synthetic benchmarks are a crowded space (Galileo, Patronus, Braintrust); we add nothing |
| `Clawford` / `Clawdex` (Claude-branded portmanteau) | Couples brand to a single LLM provider; bad for cross-provider battles |

## References

- `docs/adr/0001-stack-python-fastapi.md` — stack (unchanged)
- `docs/adr/0002-ionq-hooks-adoption.md` — guardrails (unchanged)
- `docs/adr/0003-swimlane-membership.md` — peer constellation (unchanged: role = `showcase-dogfood`)
- `docs/adr/0004-coach-hub-cache.md` — coach optimization (reframed: dev-tool, not product)
- `.harness/spec.md` — PHASE-2 scaffold scope under this ADR
- `/home/admin/gh/ionq/ionq/metaharness/` — proposer + Pareto code to wrap
- `/home/admin/gh/helios/HANDOFF_FROM_IONQ.md` — Vector A CAS substrate
- [github.com/smogon/pokemon-showdown](https://github.com/smogon/pokemon-showdown) — battle UX inspiration
- [github.com/pkmn/engine](https://github.com/pkmn/engine) — modern battle engine arch
- Live: https://agentdex.ai-builders.space · Domain: `agentdex.builders` (parked)
