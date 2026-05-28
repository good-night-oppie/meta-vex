# Anti-Reward-Hack Protocol (Inoculation)

This project enforces anti-reward-hacking guardrails. Control plane:
`.harness/` (spec, files-allowed, disclosure, optional heldout) +
`.claude/settings.json` (deny rules + UserPromptSubmit/Stop hooks) +
`.claude/agents/judge.md` (LLM judge subagent fallback).

Primary LLM judge: cursor-agent with composer-2-5 (different model family
from impl agent, mitigates same-family judge bias per Anthropic research).
Fallback: Claude SDK headless. Final fallback: fail-open.

## Disclosure Protocol (Anthropic inoculation pattern)

If you find yourself wanting to take ANY of these shortcuts:
- skip / xfail / noqa / type-ignore a failing case
- mock the system under test
- edit a fixture so it returns the expected value
- delete or rename a test out of existence
- commit with `--no-verify` / pytest with `--ignore`
- claim "done" without running fresh tests
- touch files outside `.harness/files-allowed`

…STOP. Append an entry to `.harness/disclosure.md` with a level-3 heading
starting with: `suppression:`, `test-count:`, `scope:`, `verifier:`,
`test-heavy:`. Disclosed shortcuts are flagged for human review but not
blocked. Hidden shortcuts are caught by the Stop hook and force a resume.

Research finding (Anthropic): explicit disclosure / inoculation removes
misaligned generalization that emerges when models hide reward-hacking.

## Source of truth

`.harness/spec.md` is the spec. Git diff is what you actually did. The LLM
judge compares the two. Pytest output is verified by re-running in a fresh
process — your claimed output is not trusted by the Stop hook.

Held-out tests (.harness/heldout-tests/) and held-out spec sections
(.harness/holdout-spec.md) may exist and are deny-listed for read. Don't
try to access them.

## Files you may NOT edit

`.claude/hooks/**`, `.claude/agents/**`, `.claude/settings.json`,
`.cursor/hooks/**`, `.cursor/hooks.json`,
`hooks/_ionq_hooks/**`, `.harness/spec.md`, `.harness/files-allowed`,
`.harness/test-count`, `.harness/judge.log`,
`.harness/hook-events.jsonl`, `.harness/shadow-state.json`,
`.harness/heldout-state.json`, `.harness/holdout-spec.md`,
`.harness/heldout-tests/**`, `tests/conftest.py`, `pytest.ini`,
`setup.cfg`, `.github/workflows/**`.

Deny-listed at the tool layer. If you genuinely need to change one, ask
the operator.
