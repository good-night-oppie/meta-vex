# meta-vex

VEX (Virtual EXploration) playground for the ionq · helios · oppie trio.

Hub-and-leaf swarm orchestrator on top of `ai-builders-coach` MCP. Showcases
multi-agent fan-out patterns against [space.ai-builders.com](https://space.ai-builders.com)
without N× hammering the upstream OpenAPI fetch.

## Position in the trio

| Repo | Role | Surface |
|---|---|---|
| `ionq` | Orchestration runtime + VFS | Python, SQLite, MCP server |
| `helios` | CAS substrate + fork eval | Rust, Merkle store |
| `meta-vex` | **Playground / dogfood** | Python, FastAPI, swarm hub |

meta-vex consumes both — runs swarm workloads on ionq, uses helios CAS for
deterministic fork-eval of coach-driven codegen.

## Quick start

```bash
uv sync
uv run uvicorn meta_vex.main:app --reload --port 8421
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
