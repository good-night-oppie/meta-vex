# PHASE-2 Scaffold — working plan + handoff

**Created:** 2026-05-30
**Spec:** `.harness/spec.md`
**ADR:** `docs/adr/0005-pivot-to-agent-battle-platform.md`

> Anyone (human or agent) picking up this scaffold work — read `.harness/spec.md`
> first, then this plan, then `docs/adr/0005-...`. Don't drift from the scope.

## Goal (from spec.md §Acceptance criteria)

Stand up the agent-battle runtime primitives so an end-to-end smoke test
runs: two trivial agents on a trivial task in autonomous mode, with Pareto
domination deciding the winner. No UI, no real LLM proposer, no
ladder/Elo math.

## Approach — minimum viable cut, depth-first

Build the **smoke-test slice end-to-end first** (TrajectoryTree → StopSignal
→ TurnTaker stub → engine.run_battle → Pareto → CLI), then widen each module
only as needed. Do NOT pre-build matchmaking, evolver mutation, billing, or
sota adapters in this iteration.

## Task list

### Phase 2.0 — Module skeletons (15 min)
- [x] `mkdir agentdex/modules/{agents,tasks,battles,arena,evolver}`
- [x] `mkdir agentdex/shared/`
- [x] Empty `__init__.py` in each
- [x] Update `pyproject.toml` if needed (add `aiosqlite` for checkpoint store)

### Phase 2.1 — Core contracts (Pydantic models, 30 min)
- [x] `agentdex/shared/protocols.py` — `AgentRunner`, `Scorer`, `Mutator` Protocols
- [x] `agentdex/modules/tasks/models.py` — `TaskContext`, `ScorerSpec`
- [x] `agentdex/modules/agents/models.py` — `AgentVersion` (id, parent_id, harness_blob, autonomy_policy)
- [x] `agentdex/modules/battles/stops.py` — `StopReason` enum + `StopSignal` model
- [x] `agentdex/modules/battles/result.py` — `Move` (stop, taker_response), `BattleResult` (winner, scores)
- [x] `agentdex/modules/battles/tree.py` — `Checkpoint`, `Branch`, `TrajectoryTree`

### Phase 2.2 — Checkpoint storage (SQLite fallback, 30 min)
- [x] `agentdex/shared/helios_adapter.py` — `CheckpointStore` Protocol +
  `SQLiteCheckpointStore` impl (blob storage by hash)
- [x] Tests for snapshot/restore round-trip
- [x] (Defer real helios CAS to a separate ADR-tracked task)

### Phase 2.3 — Pareto check (15 min)
- [x] `agentdex/modules/evolver/pareto.py` — `dominates(a, b, objectives)`
  returning `Domination` enum (A_DOMINATES / B_DOMINATES / TIE)
- [x] Unit tests covering: clear domination, tie, mixed (no domination)

### Phase 2.4 — TurnTaker stubs (20 min)
- [x] `agentdex/modules/battles/takers.py` — `TurnTaker` Protocol +
  `OrchestratorTurnTaker` (canned-response stub) + `HumanTurnTaker`
  (stub that hardcodes "yes/proceed")
- [x] No LLM calls, no WebSocket — pure synchronous stubs returning fixed strings
- [x] Real impls land in PHASE-3

### Phase 2.5 — Engine + trivial agents (45 min)
- [x] `agentdex/modules/agents/trivial.py` — `echo_agent_v1` (returns input
  unchanged after one stop), `echo_agent_v2` (uppercases input after one stop)
- [x] `agentdex/modules/tasks/trivial.py` — `uppercase_input` task with
  exact-match scorer
- [x] `agentdex/modules/battles/engine.py` — `async run_battle(side_a,
  side_b, taker_a, taker_b)` driving two parallel tracks until both terminal
- [x] Smoke test: 2 trivial agents on uppercase task, both takers =
  OrchestratorTurnTaker, autonomous mode, runs to terminal, Pareto returns
  v2 wins (or tie if exact-match passes for both — adjust task so v1 fails)

### Phase 2.6 — CLI extension (15 min)
- [x] Extend `agentdex/swarm/cli.py` (or move to `agentdex/cli.py`) with
  `agentdex battle <agent_a_name> <agent_b_name> --task <task_id> --mode
  autonomous` subcommand
- [x] `agentdex battle echo_agent_v1 echo_agent_v2 --task uppercase_input
  --mode autonomous` should run the smoke scenario and print JSON result

### Phase 2.7 — Verify + commit (15 min)
- [x] `uv run pytest tests/ -v` all pass
- [x] `uv run ruff check .` clean
- [x] `uv run agentdex battle echo_agent_v1 echo_agent_v2 --task uppercase_input --mode autonomous` smokes
- [x] Commit + push under single commit `feat(PHASE-2): battle engine MVP slice`
- [x] Create Linear epics GOO-13..18 mapping to new modules

## Key contracts (define once, hold the line)

```python
# agentdex/modules/battles/stops.py
class StopReason(StrEnum):
    APPROVAL_NEEDED       = "approval_needed"
    CLARIFICATION_NEEDED  = "clarification_needed"
    DIRECTION_NEEDED      = "direction_needed"
    COMPLETION_CHECK      = "completion_check"
    BLOCKED               = "blocked"

class StopSignal(BaseModel):
    reason: StopReason
    context: str
    options: list[str] | None = None
    proposed_completion: dict | None = None

# agentdex/shared/protocols.py
class AgentRunner(Protocol):
    async def run_until_stop(self, task: TaskContext, history: list[Move]) -> "AgentTurnOutput": ...
    def resume(self, taker_response: str) -> None: ...

class Scorer(Protocol):
    def score(self, task: TaskContext, agent_output: str) -> dict[str, float]: ...
    @property
    def objectives(self) -> dict[str, str]: ...  # {name: "maximize" | "minimize"}

# agentdex/modules/battles/takers.py
class TurnTaker(Protocol):
    async def respond(self, side_id: str, stop: StopSignal, history: list[Move]) -> str: ...
```

## Known pitfalls

- **Don't fall back into the swarm-dogfood framing.** This iteration is PRODUCT
  scaffold (battles), not coach optimization. Keep `agentdex/swarm/` and
  `agentdex/coach.py` untouched.
- **Don't over-build TurnTaker.** Pure stub with canned responses. Real LLM
  wiring is PHASE-3.
- **Don't build matchmaking yet.** `arena/` stays empty in this iteration.
- **Don't add evolver mutation logic.** `evolver/` only gets `pareto.py` in
  this iteration; mutation calls into ionq.metaharness are PHASE-3.
- **SQLite blob over helios CAS.** Use `~/.cache/agentdex/checkpoints.db`,
  swap to helios CAS in a later iteration without changing the
  `CheckpointStore` Protocol.
- **No conversation history in TaskContext for MVP.** `expects_human: bool`
  field is fine but `conversation: list[Message]` can be `None`. Real-task
  init via MCP is PHASE-3.
- **Frontend stays absent.** No HTML, no WebSocket, no React. CLI only.
  Visual MVP is `tail -f agentdex/.runs/<id>/{side_a,side_b}.jsonl` from
  separate terminals.
- **Per-stop fork is a tree primitive but the engine only drives ONE leaf
  path in MVP.** Forking from a past checkpoint is the data-model capability,
  not yet exposed in the engine loop. Add fork API in PHASE-3.

## Definition of done

- All 6 acceptance criteria in `.harness/spec.md` satisfied
- `bash scripts/loop_driver.sh` still ticks cleanly (heartbeat snapshot works)
- 8+ existing tests still pass; new tests added cover new code
- ADR-0005 still accurately describes the architecture (or amended if scope
  drifted with disclosure)
- This `plan.md` updated with `[x]` checkboxes as each phase completes

## Hand-off notes for resumers

If this work gets interrupted, the next session should:
1. Read `.harness/spec.md` (full PRD + acceptance criteria)
2. Read this `plan.md` and check which boxes are unchecked
3. Read `docs/adr/0005-pivot-to-agent-battle-platform.md` for product framing
4. Read `.orchestra/mailbox/agentdex.md` for CONTEXT_DUMP entries from prior sessions
5. Resume at the first unchecked phase

Memory references (for cross-session continuity):
- [[project-agentdex]] — product vision + URLs + status
- [[reference-agentdex-paths]] — integration paths + 1Password / npm details
- [[feedback-premature-framing]] — don't drift the framing
