#!/usr/bin/env bash
# Cursor preToolUse anti-cheat — runs BEFORE write tools (Edit/Write/MultiEdit).
#
# Cursor lacks Stop / PostToolUse / UserPromptSubmit / SubagentStop events.
# The Stop-hook anti-cheat referee used in Claude Code has no equivalent here,
# so this hook is more conservative: pattern-match new_string for suppression
# markers and reject *proactively*.
#
# Trade-off:
#   - Claude pack catches violations AFTER edit lands on disk (real diff)
#   - Cursor pack catches BEFORE write (proposed new_string only)
#   - Cursor pack misses cross-file scope drift, test-count regression,
#     test-vs-src ratio. Those are documented gaps in CURSOR_GAPS.md.
set -euo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool // empty')
NEW=$(echo "$INPUT" | jq -r '.args.new_string // .args.content // empty')
EDIT_PATH=$(echo "$INPUT" | jq -r '.args.file_path // .args.path // empty')

# Only inspect write tools.
case "$TOOL" in
    Edit|Write|MultiEdit|CreateFile) ;;
    *) exit 0 ;;
esac

# Verifier-tampering paths (deny edits proactively).
# Python: conftest, pytest.ini, setup.cfg, pyproject.toml
# JS/TS:  vitest.config, jest.config
# Go:     go.mod, go.sum, .golangci.yml, Makefile, *_test.go fixtures under testdata/
# CI:     .github/workflows/
case "$EDIT_PATH" in
    *tests/conftest.py|*pytest.ini|*setup.cfg|*pyproject.toml|*vitest.config*|*jest.config*|*go.mod|*go.sum|*.golangci.yml|*.golangci.yaml|*Makefile|*.github/workflows/*)
        echo "[cursor-anticheat] proactive block: edits to evaluator surface ($EDIT_PATH) are denied. If legitimate, ask operator to edit directly." >&2
        exit 2
        ;;
    */testdata/*)
        echo "[cursor-anticheat] proactive block: testdata fixtures ($EDIT_PATH) are evaluator surface. Edit via spec change, not direct fixture mutation." >&2
        exit 2
        ;;
    *.harness/spec.md|*.harness/files-allowed|*.harness/heldout-tests/*|*.harness/holdout-spec.md)
        echo "[cursor-anticheat] proactive block: $EDIT_PATH is judge/spec surface, agent-read-only." >&2
        exit 2
        ;;
esac

# Suppression-marker grep on new content.
# Python:  @pytest.mark.skip/xfail, # noqa, # type: ignore, except: pass
# JS/TS:   it.skip(, describe.skip(
# Go:      t.Skip(, t.SkipNow(, //nolint, // +build ignore, //go:build ignore
if echo "$NEW" | grep -qE '@pytest\.mark\.(skip|xfail)\(|except[[:space:]]*:[[:space:]]*pass|#\s*type:\s*ignore|#\s*noqa(\s|$)|it\.skip\(|describe\.skip\(|\bt\.Skip(Now)?[[:space:]]*\(|//[[:space:]]*nolint(\s|:|$)|//[[:space:]]*\+build[[:space:]]+ignore|//go:build[[:space:]]+ignore'; then
    REPO="${CLAUDE_PROJECT_DIR:-$PWD}"
    DISCL="$REPO/.harness/disclosure.md"
    if [ -f "$DISCL" ] && grep -qE '^###\s+suppression:' "$DISCL"; then
        # disclosed, allow
        exit 0
    fi
    echo "[cursor-anticheat] proactive block: new suppression marker in $PATH_. Fix root cause, or add '### suppression: <reason>' entry to .harness/disclosure.md first." >&2
    exit 2
fi

exit 0
