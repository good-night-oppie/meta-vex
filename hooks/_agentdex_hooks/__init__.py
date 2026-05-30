"""agentdex-hooks shared library — canonical hook chain.

Single source of truth for hook logic across the good-night-oppie
constellation (agentdex / bene / helios / oppie). The .claude/hooks/
and .cursor/hooks/ directories contain thin executable shims that
delegate here.

agentdex hosts the canonical version; bene/helios/oppie sync from
here via scripts/sync-hooks.sh (sync direction: agentdex → others).
"""
from __future__ import annotations

__version__ = "0.1.0"
