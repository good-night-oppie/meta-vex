#!/usr/bin/env bash
# Cursor preToolUse — block dangerous Bash patterns before exec.
#
# Catches what permissions.deny in Claude Code does for Bash, but Cursor's
# permission model is .cursorrules (less granular). Hook is the enforcement.
set -euo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool // empty')
CMD=$(echo "$INPUT" | jq -r '.args.command // empty')

[ "$TOOL" = "Bash" ] || exit 0
[ -n "$CMD" ] || exit 0

# Patterns we block proactively.
# Note: [^|&;] segment-anchors are best-effort — compound bypass via $(…)`,
# backtick, newline, or env-var indirection is NOT fully covered. This hook
# is a fast guardrail, not a sandbox.
#
# Categories:
#   git evasion:  --no-verify / -n / --force / --hard
#   destructive:  rm -rf of tests, testdata, .harness, internal, pkg
#   test evasion: pytest --ignore, go test -run='^$', go test -tags=skip
#   secret leak:  cat ~/.ssh, curl | sh|bash
if echo "$CMD" | grep -qE '(git commit[^|&;]*--no-verify|git commit[^|&;]*-n |git push[^|&;]*--force|git reset[^|&;]*--hard|rm -rf [^|&;]*(tests|testdata|\.harness|internal|pkg)|pytest[^|&;]*--ignore|go test[^|&;]*-run[= ]'"'"'?\^?\$'"'"'?|go test[^|&;]*-tags[= ][^[:space:]]*skip|cat[^|&;]*~/\.ssh|curl[^|&;]*\| *(sh|bash))'; then
    echo "[cursor-anticheat] proactive block: dangerous Bash pattern in '$CMD'. If legitimate, ask operator to run manually." >&2
    exit 2
fi

exit 0
