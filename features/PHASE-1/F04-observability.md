# F04 — Observability

**Phase:** 1
**Status:** pending
**Depends on:** F03

## Goal

Per-tick metrics on swarm runs surface to constellation mailbox + heartbeat.

## Deliverables

- [ ] Per-leaf timing + result-size JSONL log under `logs/swarm/`
- [ ] Coach cache hit/miss counter exposed via `/metrics` (Prometheus text)
- [ ] Mailbox `BENCH` auto-emission on each completed swarm run
- [ ] Heartbeat snapshot extended with `last_swarm_run`, `cache_hit_rate`
- [ ] Hook into `ionq-hooks` agent_metrics layer (enabled in ADR-0002)

## Exit criteria

- Read `/metrics` returns counter deltas across two consecutive runs
- Mailbox `all.md` shows BENCH entries after each run
- Heartbeat snapshot reflects most recent swarm state within 10m
