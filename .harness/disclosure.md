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

### scope: 2026-05-31 — add scripts/sync-hooks.sh (canonical → downstream propagator)

**Date:** 2026-05-31 ~10:32 PDT
**Active spec:** PHASE-2 battle engine MVP (`.harness/spec.md`).
**Plan reference:** companion to the earlier `### scope:` rename entry.
Sync script implements path B's "canonical → downstream" propagation
direction.

**Files outside `.harness/files-allowed` added:**
- `scripts/sync-hooks.sh` — 130 LOC bash. Copies agentdex's
  `_agentdex_hooks/` + `.claude/{settings.json,hooks,agents}` to peer
  repos (bene/helios/oppie) with sed-rewrite of `_agentdex_hooks` →
  `_<repo>_hooks` and `AGENTDEX_HOOKS_BASE_REF` → `<REPO>_HOOKS_BASE_REF`.
  Includes `--dry-run` and per-target skip if `.git` or `.harness`
  missing (idempotent / safe for missing targets).

**Authorization:** explicit operator turn 2026-05-31 ~10:14 PDT
("跑全部 hook sync" includes writing the sync script).

**Why this is not silent reward hacking:**
- Pure tooling addition (script never invoked automatically; runs only
  when operator explicitly executes it)
- No spec bypass / fixture mod / verifier surface edit
- Reverse op: `rm scripts/sync-hooks.sh`

**Owner:** etang via operator turn 2026-05-31 ~10:14 PDT.

### scope: 2026-05-31 — make judge.md + __init__.py repo-neutral (sync-safe content)

**Date:** 2026-05-31 ~11:22 PDT
**Active spec:** PHASE-2 battle engine MVP.
**Plan reference:** companion to prior rename + sync-script entries.
First sync-hooks.sh run revealed agentdex-specific literals (`agentdex.X`,
`agentdex hosts the canonical version; bene/helios/oppie sync from
here`) leaking into bene/helios via sync. Fixed by making source
repo-neutral so a single sync overwrite reads correctly from any repo.

**Files outside `.harness/files-allowed` touched:**
- `.claude/agents/judge.md` — DISAGREE table genericized: `<pkg>` / `<src>`
  placeholders + multi-lang examples (Py/Go/Rust/JS)
- `hooks/_agentdex_hooks/__init__.py` — docstring repurposed as "shared
  chain doc" rather than "I am the canonical, others sync from me"

**Authorization:** explicit operator turn 2026-05-31 ~11:22 PDT
("跑全部 hook sync 计划" after surfacing the leak gap).

**Why this is not silent reward hacking:**
- Pure docstring/table edit; no detector logic / scope rule / verifier surface change
- Reverse op: `git revert` this commit + revert any subsequent re-sync

**Owner:** etang via operator turn 2026-05-31 ~11:22 PDT.
