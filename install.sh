#!/usr/bin/env bash
# Idempotent install / smoke-test for ionq-hooks pack.
#
# Usage:
#   ./install.sh                       # install into current project
#   ./install.sh --smoke               # run smoke tests on freshly-installed pack
#   ./install.sh --upgrade             # re-render from upstream cookiecutter
#
# Ignore destination:
#   --exclude-mode=local       (default) write scratch ignores to
#                              .git/info/exclude — per-repo, not committed,
#                              keeps pack operator-private
#   --exclude-mode=gitignore   append to .gitignore — committed, team-shared
#   --exclude-mode=none        skip ignore step entirely
#
# Auto-detect: if .gitignore already contains a prior ionq-hooks block,
# stay in gitignore mode. Else default to local.
set -euo pipefail

cd "$(dirname "$0")"

MODE="install"
EXCLUDE_MODE=""
for arg in "$@"; do
    case "$arg" in
        --smoke|--upgrade)      MODE="$arg" ;;
        install)                MODE="install" ;;
        --exclude-mode=*)       EXCLUDE_MODE="${arg#*=}" ;;
        *)                      echo "unknown arg: $arg" >&2; exit 2 ;;
    esac
done

case "$MODE" in
    --smoke) MODE="smoke" ;;
    --upgrade) MODE="upgrade" ;;
esac

case "$MODE" in
    install)
        echo "[install] chmod +x hooks…"
        find .claude/hooks .cursor/hooks -type f \( -name '*.sh' -o -name '*.py' \) -exec chmod +x {} \; 2>/dev/null || true

        echo "[install] ensure .harness/ files-allowed + spec.md exist…"
        [ -f .harness/spec.md ] || cp .harness/spec.md.example .harness/spec.md 2>/dev/null || true

        # Sentinel: any line containing "ionq-hooks" in the ignore file means
        # a managed block (or operator-curated block) is already present.
        # Detection is intentionally broad: matches both the install.sh
        # scratch comment (`# ionq-hooks scratch`) and an operator-written
        # broader block (e.g. `# ionq-hooks pack (operator-local; ...)`).
        IGNORE_SENTINEL="ionq-hooks"

        # Auto-detect exclude mode if not set explicitly.
        if [ -z "$EXCLUDE_MODE" ]; then
            if grep -qF "$IGNORE_SENTINEL" .gitignore 2>/dev/null; then
                EXCLUDE_MODE="gitignore"   # legacy / team install already used .gitignore
            else
                EXCLUDE_MODE="local"       # operator-private default
            fi
        fi

        # Scratch ignores written to chosen destination.
        IGNORE_BLOCK='
# ionq-hooks scratch
.harness/test-count
.harness/judge.log
.harness/hook-events.jsonl
.harness/shadow-state.json
.harness/heldout-state.json
.harness/test-result.json
hooks/_ionq_hooks/__pycache__/
.claude/hooks/__pycache__/'

        case "$EXCLUDE_MODE" in
            local)
                EXCL=".git/info/exclude"
                if [ ! -f "$EXCL" ]; then
                    echo "[install] $EXCL not writable; skipping ignore step."
                elif grep -qF "$IGNORE_SENTINEL" "$EXCL"; then
                    echo "[install] $EXCL already has an ionq-hooks block; skipping ignore step."
                else
                    echo "[install] writing scratch ignores to $EXCL (operator-local)…"
                    printf '%s\n' "$IGNORE_BLOCK" >> "$EXCL"
                fi
                ;;
            gitignore)
                if grep -qF "$IGNORE_SENTINEL" .gitignore 2>/dev/null; then
                    echo "[install] .gitignore already has an ionq-hooks block; skipping ignore step."
                else
                    echo "[install] appending scratch ignores to .gitignore (team-shared)…"
                    printf '%s\n' "$IGNORE_BLOCK" >> .gitignore
                fi
                ;;
            none)
                echo "[install] --exclude-mode=none; skipping ignore step."
                ;;
            *)
                echo "[install] invalid --exclude-mode=$EXCLUDE_MODE (want local|gitignore|none)" >&2
                exit 2
                ;;
        esac

        echo "[install] (optional) install pytest reporter…"
        if [ -d reporters/pytest ] && command -v uv >/dev/null 2>&1; then
            uv pip install -e reporters/pytest >/dev/null 2>&1 || true
        elif [ -d reporters/pytest ] && command -v pip >/dev/null 2>&1; then
            pip install -e reporters/pytest >/dev/null 2>&1 || true
        fi

        echo "[install] verify _ionq_hooks Python source landed…"
        py_count=$(ls hooks/_ionq_hooks/*.py 2>/dev/null | wc -l)
        if [ "$py_count" -lt 10 ]; then
            echo "[install] FAIL: expected >=10 .py files in hooks/_ionq_hooks, found $py_count." >&2
            echo "[install] Re-render template or copy source files manually." >&2
            exit 1
        fi
        echo "[install]   ✓ $py_count .py files present"

        echo "[install] done."
        echo "Next: fill .harness/spec.md, edit .harness/files-allowed, start your agent."
        ;;

    smoke)
        echo "[smoke] verify hook syntax…"
        python3 -m py_compile .claude/hooks/stop-integrity-check.py
        python3 -m py_compile hooks/_ionq_hooks/*.py
        bash -n .claude/hooks/spec-injector.sh 2>/dev/null && echo "  ✓ spec-injector.sh"
        [ -d .cursor ] && { bash -n .cursor/hooks/pre-edit-anticheat.sh && echo "  ✓ pre-edit-anticheat.sh"; }
        [ -d .cursor ] && { bash -n .cursor/hooks/pre-bash-anticheat.sh && echo "  ✓ pre-bash-anticheat.sh"; }
        [ -d .cursor ] && { bash -n .cursor/hooks/session-start.sh && echo "  ✓ session-start.sh"; }

        echo "[smoke] dry-run spec-injector…"
        CLAUDE_PROJECT_DIR="$PWD" .claude/hooks/spec-injector.sh < /dev/null | head -5

        echo "[smoke] dry-run stop hook on clean tree…"
        echo '{}' | CLAUDE_PROJECT_DIR="$PWD" timeout 10 .claude/hooks/stop-integrity-check.py > /tmp/ionq-hook-smoke.txt 2>&1 || true
        echo "  exit=$? (expect 0 on clean tree; non-zero is fine if you're in the middle of a task)"

        echo "[smoke] all good."
        ;;

    upgrade)
        echo "[upgrade] not implemented; re-run cookiecutter from source repo."
        exit 1
        ;;

    *)
        echo "usage: $0 [install|--smoke|--upgrade] [--exclude-mode=local|gitignore|none]"
        exit 1
        ;;
esac
