# Architecture

> Placeholder. Replaced by `tech-lead:design` output on first lifecycle pass.

## High level

```
                        ┌─────────────────────┐
                        │  ai-builders-coach  │  ← MCP server (upstream)
                        │   space.ai-builders │
                        └──────────┬──────────┘
                                   │ single fetch
                                   ▼
            ┌──────────────────────────────────────────┐
            │  meta_vex.coach.CoachCache (hub-only)    │
            │  /tmp/meta-vex/coach-spec.json + ETag    │
            └──────────────────────────────────────────┘
                                   │ read cached slice
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │  leaf_1    │       │  leaf_2    │  ...  │  leaf_N    │
       │  endpoint  │       │  schema    │       │  codegen   │
       │  reasoning │       │  validate  │       │            │
       └────────────┘       └────────────┘       └────────────┘
```

## Decisions

See `docs/adr/` (populated by `tech-lead:adr` runs).

## Cross-trio role

- **ionq:** provides VFS + agent execution loop; meta-vex leaves run inside ionq agents
- **helios:** provides CAS substrate for K-way speculative fork eval of leaf outputs
- **oppie:** trio-meta layer; meta-vex feeds dogfood signal back to oppie roadmap
