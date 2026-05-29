# Active spec — Agentdex PHASE-2 scaffold

## Product (PRD summary)

**Agentdex** = Pokémon Showdown for AI agents.

- Two agents face off split-screen on **real tasks** (the human's current work,
  not synthetic benchmarks)
- Each natural stop signal (approval / clarification / direction / completion
  check) is a **checkpoint** — the user picks per-stop whether *they* engage or
  let the **proposer LLM** take over
- Stops form a **trajectory tree** rooted at task init; forks allowed from any
  past checkpoint → multiple alternate trajectories
- **Pareto domination** decides battle winners (accuracy × cost × speed)
- **MetaHarness** mutates agents whose new candidate Pareto-dominates incumbent

See `docs/adr/` (0001–0004 current; ADR-0005 documenting the pivot is pending).

## Current task — PHASE-2 module scaffold

Stand up the battle runtime primitives. No UI, no SOTA adapters, no billing.

### Modules to create

```
agentdex/modules/
├── agents/     # Agent identity + versions + lineage (wraps ionq HarnessCandidate)
├── tasks/      # TaskContext + scorer registry
├── battles/    # TrajectoryTree, Checkpoint, StopSignal, TurnTaker, Engine
├── arena/      # (stub) ladder + per-objective Elo
├── evolver/    # (stub) wraps ionq.MetaHarnessSearch + Pareto check
└── shared/
    ├── protocols.py     # AgentRunner, Scorer, Mutator
    ├── helios_adapter.py # checkpoint storage (helios CAS OR SQLite blob fallback)
    └── ionq_adapter.py   # bridges agentdex.AgentVersion ↔ ionq.HarnessCandidate
```

## Acceptance criteria (PHASE-2 MVP slice)

1. `agentdex.modules.battles.tree.TrajectoryTree` + `Checkpoint` + `Branch` models
   with snapshot/restore round-trip via `helios_adapter` (SQLite blob backend OK
   for MVP).
2. `agentdex.modules.battles.stops.StopSignal` Pydantic contract +
   `agentdex.modules.battles.takers.{HumanTurnTaker, OrchestratorTurnTaker}`
   stub implementations.
3. `agentdex.modules.battles.engine.run_battle()` runs two trivial agents in
   parallel asyncio task group, drives them via TurnTakers, captures Moves as
   tree branches.
4. `agentdex.modules.evolver.pareto.dominates(a, b, objectives)` returns
   Pareto-domination verdict.
5. End-to-end smoke test: 2 trivial agents (`echo_agent_v1`, `echo_agent_v2`) on
   1 trivial task (`uppercase_input`), autonomous mode (both takers =
   OrchestratorTurnTaker), runs to terminal, Pareto check returns winner OR tie.
6. CLI: `agentdex battle <agent_a> <agent_b> --task <id> --mode autonomous`
   (extends existing `swarm` CLI registry).

## Visual effect — keep simple

For now, the "split-screen battle" can be as plain as:
- two stacked terminal panes (side A above, side B below, tail -f the move logs)
- a single HTML page with two `<pre>` blocks polling the battle endpoint
- JSON logs streamed to stdout

Do NOT spend cycles on fancy animations, WebSocket React UI, OG card image
generation, Twitter cards, Tailwind themes, or canvas-based replays in this
iteration. Plain text > nothing. Pretty UI is PHASE-4 work, not now.

## Out of scope (do NOT touch this iteration)

- Frontend / split-screen UI (PHASE-4)
- Twitter / social share (PHASE-4)
- Billing (PHASE-5)
- Real LLM-driven proposer in `OrchestratorTurnTaker` — keep it as a stub that
  returns canned responses; real wiring is PHASE-3
- Helios CAS hard requirement — SQLite blob fallback is fine for MVP
- Matchmaking / Elo ladder math (PHASE-3 stub OK, no impl needed yet)
- HumanTurnTaker WebSocket prompting — stub returning hardcoded responses OK
- New ai-builders-coach MCP integrations beyond what's already in
  `agentdex/coach.py`
- Renaming existing `agentdex/swarm/` (keep it — it's the parallel-branch
  executor for the tree)

## Non-goals

- Don't reimplement `ionq.metaharness.*` — import and wrap
- Don't build a second coach MCP client — reuse `agentdex.coach.CoachCache`
- Don't add a frontend in this iteration — even a simple HTML page (defer all UI)
- Don't write ADR-0005 in this iteration unless explicitly asked — it's its own
  task

## Definition of done

- All visible AND held-out tests pass.
- No new `@pytest.mark.skip` / `xfail` / `# noqa` / `# type: ignore` unless
  disclosed in `.harness/disclosure.md` with a reason.
- Only files in `.harness/files-allowed` modified.
- LLM judge returns `VERDICT: AGREE`.
- `pyproject.toml` updated if new deps added (e.g. `aiosqlite` for blob storage).
- README + relevant ADRs reflect changes (PHASE-1 ADRs need no edits; if you
  add ADR-0006+ for a new decision, fine).
- `agentdex battle ...` CLI smokes against the trivial scenario in §5.

## Reference (load these before working)

- `docs/adr/0001-stack-python-fastapi.md` — stack choice
- `docs/adr/0002-ionq-hooks-adoption.md` — guardrails
- `docs/adr/0003-swimlane-membership.md` — peer constellation + mailbox protocol
- `docs/adr/0004-coach-hub-cache.md` — historical coach optimization
  (still correct, but coach is now build-time/dev-tool, not product layer)
- `features/PHASE-1/` — existing F01–F04 specs (PHASE-1 mostly done)
- `~/gh/ionq/ionq/metaharness/` — wrap this, don't reimplement

When in doubt about scope, post a ## CONTEXT_DUMP to
`.orchestra/mailbox/agentdex.md` and stop.
