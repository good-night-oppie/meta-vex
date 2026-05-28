# Cursor-flavor gaps vs Claude Code

ionq-hooks ships REDUCED guardrails for Cursor because Cursor's hook surface
is a strict subset of Claude Code's. This file documents what's missing and
why, so operators don't assume parity.

## Hook-event coverage

| Event | Claude Code | Cursor |
|---|---|---|
| `UserPromptSubmit` (every turn) | ✅ | ❌ |
| `SessionStart` (once per boot) | ✅ | ✅ (camelCase: `sessionStart`) |
| `PreToolUse` (before each tool call) | ✅ | ✅ (camelCase: `preToolUse`) |
| `PostToolUse` (after each tool call) | ✅ | ❌ |
| `beforeShellExecution` (before bash exec) | ❌ | ✅ |
| `Stop` (after agent declares done) | ✅ | ❌ |
| `SubagentStop` | ✅ | ❌ |
| `PreCompact` (before context compaction) | ✅ | ❌ |
| `Notification` (when agent waits for user) | ✅ | ❌ |

## Pack feature coverage

| Pack feature | Claude flavor | Cursor flavor | Notes |
|---|---|---|---|
| Spec injection every turn (Layer D) | ✅ via UserPromptSubmit | ⚠ once-only via sessionStart | Restart session on spec.md change |
| Inoculation protocol (Layer E) | ✅ injected per turn | ⚠ injected at session boot only | Same caveat |
| Deny rules (Layer A) | ✅ via permissions.deny | ⚠ via preToolUse regex | Less granular |
| Suppression-marker detection (Layer F) | ✅ Stop hook on real diff | ⚠ proactive preToolUse on new_string | Misses MultiEdit corner cases |
| Verifier-tampering detection | ✅ Stop hook | ✅ preToolUse path-match | Equivalent |
| Scope-drift detection | ✅ Stop hook + files-allowed | ❌ | No way to see cross-file diff in preToolUse |
| Test-count regression | ✅ Stop hook | ❌ | No post-completion test invocation |
| Test-vs-src ratio | ✅ Stop hook | ❌ | Needs cross-file diff |
| LLM judge (composer-2-5) | ✅ Stop hook | ❌ | No Stop event to trigger |
| Heldout sampling | ✅ Stop hook | ❌ | No Stop event |
| Telemetry log | ✅ orchestrator-emitted | ⚠ per-hook only | Sparser data |
| Shadow-mode promotion | ✅ in orchestrator | ❌ | preToolUse hooks fire-and-forget |
| Disclosure escape hatch | ✅ honored in all detectors | ✅ honored in suppression detector only | |

## When to use which flavor

- **Use Claude flavor** when full anti-reward-hack coverage matters (golden
  datasets, evaluation pipelines, security-critical refactors).
- **Use Cursor flavor** when you need basic safety (no `--no-verify`, no
  suppression markers slipping through), and operator is doing the heavy
  lifting on spec / test discipline.
- **Use both flavors** for repos where some operators run Claude and others
  run Cursor; the harness reads `.harness/` regardless of which agent fired.

## Bridging the Stop-hook gap (CI fallback)

Cursor users who want anti-cheat coverage without Stop-hook semantics can
add a pre-commit hook (git, not agent) that runs `.harness/anti-cheat-ci.sh`:

```bash
# .git/hooks/pre-commit
exec .harness/anti-cheat-ci.sh
```

The CI fallback runs the same orchestrator but synchronously at commit
time instead of agent-done time. Less responsive but covers the gap.

## Roadmap

If Cursor adds a `stop` / `agentDone` event in a future release (track
[Cursor changelog](https://cursor.com/changelog)), we'll add it here.
