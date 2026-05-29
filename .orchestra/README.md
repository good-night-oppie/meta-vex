# .orchestra/ — multi-session mailbox

Implements the [ionq Multi-Session Overcommunication Protocol](../CLAUDE.md#multi-session-overcommunication-protocol).

```
mailbox/
├── agentdex.md   ← inbox for THIS session
├── all.md        ← broadcasts visible to entire constellation
└── <peer>.md     ← (created on first message to that peer)
```

### Convention

- One markdown section per message, dated, signed with originating session
- Never edit prior messages — append only
- ACK by appending an `ACK` section, do not delete
- Heartbeat snapshot at `~/.cursor/projects/home-etang/heartbeat/snapshots/agentdex.txt`
  mirrors the session state every loop tick
