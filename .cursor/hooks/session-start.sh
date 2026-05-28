#!/usr/bin/env bash
# Cursor sessionStart — print spec + protocol + scope ONCE per session.
#
# Unlike Claude's UserPromptSubmit (fires every turn), this fires only at
# session boot. Spec is less aggressively-resident. Operator should re-load
# the session whenever spec.md changes.
set -euo pipefail

REPO="${CURSOR_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$PWD}}"
HARNESS="$REPO/.harness"

[ -f "$HARNESS/spec.md" ] || exit 0

if [ -f "$HARNESS/REWARD_HACK_PROTOCOL.md" ]; then
    cat "$HARNESS/REWARD_HACK_PROTOCOL.md"
    echo ""
fi

echo "## Active spec (session-start injection — Cursor lacks per-prompt inject)"
echo ""
head -n 80 "$HARNESS/spec.md"
echo ""

[ -f "$HARNESS/files-allowed" ] && {
    echo "## In-scope files"
    grep -v '^\s*#' "$HARNESS/files-allowed" | grep -v '^\s*$' | head -n 40
    echo ""
}

echo "## Reminder — Cursor-flavor caveats"
echo "- preToolUse anti-cheat blocks edits to evaluator surfaces + suppression markers."
echo "- NO Stop hook, NO LLM judge, NO test-count regression, NO scope-drift detector."
echo "- For full pack run this project in Claude Code instead. See CURSOR_GAPS.md."
