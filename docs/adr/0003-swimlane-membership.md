# ADR-0003: Swimlane membership in ionq constellation

**Date:** 2026-05-28
**Status:** Accepted

## Context

The ionq trio runs a multi-session tmux constellation (`ionq`, `helios`,
`oppie`, `cursor`, `cr`, `triage`, `ui`). Each session keeps a mailbox at
`<repo>/.orchestra/mailbox/`. Cross-session contracts: bug surfacing,
handoffs, broadcasts, heartbeat.

## Decision

agentdex joins the constellation as session **`agentdex`** with role
**Showcase / Dogfood Lane**.

| Mailbox file | Purpose |
|---|---|
| `agentdex.md` | Inbox |
| `all.md` | Broadcast to all peers |
| `ionq.md` | Direct to ionq (bug surfacing, runtime questions) |
| `helios.md` | Direct to helios (CAS / fork-eval) |
| `cursor.md` | Direct to meta-planner (strategic) |

Heartbeat snapshot location:
`~/.cursor/projects/home-etang/heartbeat/snapshots/agentdex.txt`,
written by `scripts/loop_driver.sh` on every tick.

## Consequences

- Existing peers can address agentdex without ad-hoc plumbing
- agentdex's job to drain inbox + ack on every prompt (per CLAUDE.md)
- Constellation heartbeat sweep picks up agentdex automatically
