# Reward-hack disclosure log

> Write a tagged entry BEFORE the Stop hook runs if you take a shortcut.
> Disclosed shortcuts are flagged but not blocked. Hidden shortcuts → block.
>
> Each entry MUST be a level-3 heading with one of these tokens:
> ```
> ### suppression:   skip / xfail / noqa / type:ignore
> ### test-count:    intentional test removal/rename
> ### scope:         touching files outside files-allowed
> ### verifier:      editing conftest/pyproject/workflows
> ### test-heavy:    refactors that touch tests >> src
> ```
> Token list above is documentation; matcher ignores it.

---

<!-- add real entries below this line -->

### scope: 2026-05-31 — rename hooks/_ionq_hooks → hooks/_agentdex_hooks (canonical hook source)

**Date:** 2026-05-31 ~10:21 PDT
**Active spec:** PHASE-2 battle engine MVP.
**Plan reference:** good-night-oppie constellation hook sync (path B in
the multi-repo plan): agentdex is canonical hook source-of-truth;
bene/helios/oppie sync FROM agentdex.

**Files outside `.harness/files-allowed` that were touched:**
- `hooks/_ionq_hooks/**` → `hooks/_agentdex_hooks/**` (git mv, full pkg rename)
- `hooks/_agentdex_hooks/__init__.py` — docstring updated to "agentdex-hooks shared library — canonical hook chain"
- `hooks/_agentdex_hooks/paths.py` — `hooks_dir()` returns `_agentdex_hooks`
- `hooks/_agentdex_hooks/judge.py` — env var `IONQ_HOOKS_BASE_REF` → `AGENTDEX_HOOKS_BASE_REF`
- `hooks/_agentdex_hooks/git_state.py` — same env var rename
- `.claude/settings.json` — deny rule `_ionq_hooks` → `_agentdex_hooks`
- `.claude/hooks/stop-integrity-check.py` — ancestor walk + import → `_agentdex_hooks`
- `.claude/agents/judge.md` — DISAGREE table `ionq.X` → `agentdex.X`

**Authorization:** explicit operator turn 2026-05-31 ~10:14 PDT, request:
"路径 B — uniform `_<repo>_hooks` + agentdex 当源 (\"居中\" 字面贯彻)"
followed by "跑全部 hook sync".

**Why this is not silent reward hacking:**
- Pure rename + adapt operation, no test bypass / fixture mod / verifier
  edit
- Stop hook dry-run confirms shadow-detected as scope-drift but
  fail-open (shadow not promoted)
- Future canonical of hook code lives in agentdex; bene/helios/oppie
  will sync from here. ionq decommission underway (bene successor).
- Reverse op: `git mv hooks/_agentdex_hooks/ hooks/_ionq_hooks/` + sed
  on the 6 ref files.

**Doctrine:** uniform `_<repo>_hooks` naming + agentdex as canonical
source.

**Note on `.harness/files-allowed`:** The current files-allowed scopes
agentdex's PHASE-2 battle engine spec, NOT this hook refactor. Operator
authorized scope-creep for this one-off rename pass. files-allowed
itself is NOT modified by this disclosure entry (operator-only meta-file).

**Owner:** etang via operator turn 2026-05-31 ~10:14-10:21 PDT.
