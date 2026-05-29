# agentdex

🌐 Live at **[agentdex.ai-builders.space](https://agentdex.ai-builders.space)**
(custom domain `agentdex.builders` parked, CNAME later).

**Pokémon Showdown for AI agents.** Two agents face off split-screen on real
tasks; checkpoints at every natural stop become forkable trajectories; Pareto
domination decides winners; MetaHarness evolves agents that beat their lineage.

> Status: PHASE-1 scaffold in place (FastAPI + swarm runtime + ionq-hooks +
> ai-builders-coach MCP integration). Battle engine + frontend pending.
> See `docs/adr/` for design decisions.

## Position in the trio

| Repo | Role | Surface |
|---|---|---|
| `ionq` | Orchestration runtime + VFS | Python, SQLite, MCP server |
| `helios` | CAS substrate + fork eval | Rust, Merkle store |
| `agentdex` | **Playground / dogfood** | Python, FastAPI, swarm hub |

agentdex consumes both — runs swarm workloads on ionq, uses helios CAS for
deterministic fork-eval of coach-driven codegen.

## Quick start

```bash
uv sync
uv run uvicorn agentdex.main:app --reload --port 8421
uv run python -m pytest tests/ -v
```

## Swarm shape

```
hub (orchestrator)
  ├─ fetch_spec_once → /tmp/coach-spec.json (cached, ETag-aware)
  ├─ leaf_1: endpoint codegen on spec slice
  ├─ leaf_2: schema validation on spec slice
  └─ leaf_N: ...
```

Single coach MCP call at hub; leaves read cached artifact. Avoids stdio
serial-queue, N× token burn, and 429 from upstream rate limit.

## License

MIT. See `LICENSE`.
