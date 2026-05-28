# ADR-0002: Adopt ionq-hooks anti-reward-hack pack

**Date:** 2026-05-28
**Status:** Accepted

## Context

meta-vex's value depends on swarm workloads producing real fix-attempts
against coach API endpoints. AI agents writing those fixes can reward-hack
(disable tests, scope-drift, fake-pass) without guardrails.

## Decision

Generate the `ionq-hooks` cookiecutter pack at scaffold time with:

| Var | Value | Reason |
|---|---|---|
| `target_agent` | `both` (claude + cursor) | Dogfood both surfaces meta-vex showcases |
| `test_runner` | `pytest` | Matches stack (see ADR-0001) |
| `judge_model` | `claude-sonnet-4-6` | No `op` dep needed, fewer external surfaces |
| `enable_heldout_sampling` | `yes` (15%) | Catch heldout regressions without 100% cost |
| `enable_shadow_mode` | `yes` (promote after 20) | Same as ionq sibling |
| `enable_agent_metrics` | `yes` | Feeds the observability ADR |

## Consequences

- `.claude/`, `.cursor/`, `.harness/`, `hooks/_ionq_hooks/` shipped from day 1
- Stop / PostToolUse / UserPromptSubmit guardrails fire on agent edits
- Upstream `ionq-hooks` bugs surface to meta-vex first (already filed one
  via `.orchestra/mailbox/ionq.md`); cycle benefits both repos
