# F01 — Foundation

**Phase:** 1
**Status:** in-progress
**Depends on:** —

## Goal

Repo scaffolds cleanly, CI green, swimlane wired, ionq-hooks active.

## Deliverables

- [x] Python (uv) skeleton with `agentdex/` package
- [x] FastAPI `/health` + identity routes
- [x] `.orchestra/mailbox/` + role doc in `CLAUDE.md`
- [x] ionq-hooks pack generated (`.claude/`, `.cursor/`, `.harness/`, `hooks/`)
- [x] `scripts/loop_driver.sh` (4 lanes) + heartbeat snap
- [x] CI workflow (ruff + mypy + pytest + coverage)
- [x] 4 foundational ADRs (stack, hooks, swimlane, coach-cache)
- [ ] Remote repo `good-night-oppie/agentdex` public + first push
- [ ] CI green on first push
- [ ] Linear project + epic created

## Exit criteria

- `uv run pytest -v` → all pass
- `bash scripts/loop_driver.sh` → tick completes, heartbeat snapshot written
- `bash install.sh --smoke` → all hooks syntax-valid
- GH Actions run on `main` → green
