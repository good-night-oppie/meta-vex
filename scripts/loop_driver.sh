#!/usr/bin/env bash
# meta-vex /loop driver.
#
# Drives four lanes on each tick (intended cadence: 10m via /loop skill):
#   1. Linear poll      — sync issue state → features/PHASE-*/*.md
#   2. Lifecycle stage  — advance tech-lead pipeline if exit criteria met
#   3. CI babysit       — surface failed GH Actions runs
#   4. Heartbeat snap   — write state to ~/.cursor/.../snapshots/meta-vex.txt
#
# Invoke via:
#   /loop 10m bash ~/gh/meta-vex/scripts/loop_driver.sh
#
# Or standalone (one tick):
#   ./scripts/loop_driver.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HEARTBEAT_DIR="${HOME}/.cursor/projects/home-etang/heartbeat"
SNAPSHOT="${HEARTBEAT_DIR}/snapshots/meta-vex.txt"
MAILBOX_DIR="${REPO_ROOT}/.orchestra/mailbox"
LINEAR_TEAM_ID="8bfc8ed9-987f-421a-bc75-527e2613d8a8"  # Good Night Oppie LLC

mkdir -p "$(dirname "$SNAPSHOT")"

log() { printf '[%s] %s\n' "$TS" "$*"; }

# ---------- Lane 1: Linear poll ----------
lane_linear() {
  log "lane=linear poll team=$LINEAR_TEAM_ID"
  # Hand off to Claude with linear-server MCP; this script writes a directive
  # the loop tick picks up. Actual API calls go through MCP, not raw curl.
  cat > "${MAILBOX_DIR}/.directives/linear.md" <<EOF
## DIRECTIVE @ $TS
poll Linear team $LINEAR_TEAM_ID, sync any state changes into features/PHASE-*/*.md
EOF
}

# ---------- Lane 2: Lifecycle stage ----------
lane_lifecycle() {
  log "lane=lifecycle check"
  local stage_file="${REPO_ROOT}/.orchestra/STAGE"
  if [[ ! -f "$stage_file" ]]; then
    echo "design" > "$stage_file"
  fi
  log "lane=lifecycle current=$(cat "$stage_file")"
}

# ---------- Lane 3: CI babysit ----------
lane_ci() {
  log "lane=ci check"
  if ! command -v gh >/dev/null 2>&1; then
    log "lane=ci skip (no gh)"; return
  fi
  if ! git remote get-url origin >/dev/null 2>&1; then
    log "lane=ci skip (no origin)"; return
  fi
  gh run list --limit 5 --json status,conclusion,name,headBranch,createdAt \
    2>/dev/null > "${MAILBOX_DIR}/.directives/ci-runs.json" || true
}

# ---------- Lane 4: Heartbeat ----------
lane_heartbeat() {
  log "lane=heartbeat write $SNAPSHOT"
  local branch
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
  local commit
  commit="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
  local stage
  stage="$(cat "${REPO_ROOT}/.orchestra/STAGE" 2>/dev/null || echo 'design')"
  local mailbox_unread
  mailbox_unread="$(awk '/^## / {c++} END {print c+0}' "${MAILBOX_DIR}/meta-vex.md" 2>/dev/null || printf 0)"

  cat > "$SNAPSHOT" <<EOF
session: meta-vex
role: showcase-dogfood
ts: $TS
branch: $branch
commit: $commit
stage: $stage
mailbox_msgs: $mailbox_unread
repo: good-night-oppie/meta-vex
trio: ionq · helios · oppie
EOF
}

mkdir -p "${MAILBOX_DIR}/.directives"

lane_linear
lane_lifecycle
lane_ci
lane_heartbeat

log "tick done"
