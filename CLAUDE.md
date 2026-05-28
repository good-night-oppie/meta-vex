# meta-vex — VEX Playground

## Project Overview
meta-vex is the dogfood / showcase lane for the `ionq · helios · oppie` trio.
Hub-and-leaf swarm on top of `ai-builders-coach` MCP. Exercises agentic
patterns against `space.ai-builders.com` without N× hammering the upstream.

## Package & CLI
- Package: `meta_vex` (import with `from meta_vex import ...`)
- HTTP entry: `uv run uvicorn meta_vex.main:app --port 8421`
- Config: env vars (see `meta_vex/coach.py`)

## Running
```bash
uv sync                                          # install deps
uv run uvicorn meta_vex.main:app --reload        # dev server
uv run python -m pytest tests/ -v                # tests
./scripts/loop_driver.sh                         # /loop driver (Linear + lifecycle + CI)
```

## Architecture
```
meta_vex/main.py            → FastAPI app, /health, /vex/* routes
meta_vex/coach.py           → ai-builders-coach MCP client, spec cache, ETag
meta_vex/swarm/hub.py       → hub orchestrator, fan-out planner
meta_vex/swarm/leaf.py      → leaf worker, reads cached spec slice
meta_vex/playground/        → VEX UI routes (canvas / preview)
```

## Rules
- Always use `uv` for Python package management
- Tests: `uv run python -m pytest tests/ -v`
- Coach MCP `get_api_specification` is fetched ONCE per session at hub;
  leaves read cached artifact. Never fan-out the spec fetch.

---

## Multi-Session Overcommunication Protocol

This session (`meta-vex`) is part of the ionq trio constellation.

### Your Identity
- **Session name:** `meta-vex`
- **Role:** **Showcase / Dogfood Lane** — exercises swarm patterns,
  surfaces real-world bugs in ionq runtime + coach MCP
- **Peers:** `ionq` (orchestrator), `helios` (CAS), `oppie` (trio meta),
  `cursor` (meta-planner), `cr` / `triage` / `ui` (constellation)

### Showcase-Lane Duties
- Build minimum-viable swarm workloads against ai-builders-coach
- Surface bugs / friction in upstream runtimes (ionq, helios) to their mailboxes
- Capture before/after benchmarks for proposed coach MCP improvements
- Never block on cross-lane work — file mailbox HANDOFF, keep moving

### Mandatory Broadcasts

```bash
MAILBOX=~/gh/meta-vex/.orchestra/mailbox
```

**On surfacing a coach / ionq / helios bug:**
Append to `$MAILBOX/<peer>.md`:
```markdown
## BUG from meta-vex @ {timestamp}
**Subject:** {one-line summary}
**Repro:** {minimal command/snippet}
**Impact on meta-vex:** {what we can't do}
**Suggested fix direction:** {optional}
```

**On shipping a swarm benchmark result:**
Append to `$MAILBOX/all.md`:
```markdown
## BENCH from meta-vex @ {timestamp}
**Workload:** {name}
**Before:** {metrics}
**After:** {metrics}
**Artifact:** {path}
```

**On needing strategic direction:**
Append to `$MAILBOX/cursor.md`

### On Every New Prompt
1. Read `$MAILBOX/meta-vex.md` — messages for you
2. Read `$MAILBOX/all.md` — broadcasts
3. Read `~/.cursor/projects/home-etang/heartbeat/digest.md` — system state
4. ACK or act on pending messages

### Before `/clear` or Context Overflow
Write CONTEXT_DUMP to `$MAILBOX/meta-vex.md`:
```markdown
## CONTEXT_DUMP from meta-vex @ {timestamp}
**Current task:** ...
**Branch:** ...
**Key decisions:** ...
**Files modified:** ...
**Next steps:** ...
```

### Peer Sessions

| Session | Repo | Role |
|---------|------|------|
| `cursor` | Cursor IDE | Meta-planner — strategic direction |
| `ionq` | `~/gh/ionq` | Orchestrator runtime owner |
| `helios` | `~/gh/helios` | CAS substrate owner |
| `oppie` | `~/gh/oppie` | Trio meta / cross-cutting |
| `cr` | `triage-rag-codeleash-a` | Feature lead — advisory workflow |
| `triage` | `src-fresh` | Unblocker |

---

## ai-builders-coach MCP rules

- `get_api_specification` returns 3,553+ lines — exceeds Claude tool-result
  max token cap, auto-spills to `tool-results/*.txt`. **Fetch once at hub**,
  persist to `/tmp/coach-spec.json`, leaves Read-with-offset.
- Upstream `space.ai-builders.com` rate-limits at unknown threshold (saw
  429s at low N). Cache aggressively.
- Author 鸭哥 is shipping granular tools (`list_endpoints`, `get_endpoint`,
  `get_schema`) — when available, leaves can call directly without hub cache.
