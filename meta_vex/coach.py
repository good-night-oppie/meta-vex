"""ai-builders-coach MCP client wrapper.

Hub-side cache pattern: spec fetched ONCE per process, persisted to disk,
leaves read cached artifact. Avoids:
- MCP stdio serial-queue (single pipe, no multiplexing)
- N x token burn on 3,553-line spec
- Upstream 429 from space.ai-builders.com rate limit
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import httpx

DEFAULT_CACHE_DIR = Path(os.getenv("META_VEX_CACHE_DIR", "/tmp/meta-vex"))
DEFAULT_BASE_URL = os.getenv("COACH_BASE_URL", "https://space.ai-builders.com")
SPEC_CACHE_PATH = DEFAULT_CACHE_DIR / "coach-spec.json"
SPEC_ETAG_PATH = DEFAULT_CACHE_DIR / "coach-spec.etag"


class CoachCache:
    """Single-fetch cache for coach OpenAPI spec.

    Use at hub layer only. Leaves read SPEC_CACHE_PATH directly.
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL, cache_dir: Path = DEFAULT_CACHE_DIR):
        self.base_url = base_url
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_spec(self, *, force: bool = False) -> dict[str, Any]:
        if not force and SPEC_CACHE_PATH.exists():
            return json.loads(SPEC_CACHE_PATH.read_text())

        headers: dict[str, str] = {}
        if SPEC_ETAG_PATH.exists() and not force:
            headers["If-None-Match"] = SPEC_ETAG_PATH.read_text().strip()

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self.base_url}/openapi.json", headers=headers)

        if resp.status_code == 304 and SPEC_CACHE_PATH.exists():
            return json.loads(SPEC_CACHE_PATH.read_text())

        resp.raise_for_status()
        spec = resp.json()
        SPEC_CACHE_PATH.write_text(json.dumps(spec, indent=2))
        if etag := resp.headers.get("etag"):
            SPEC_ETAG_PATH.write_text(etag)
        return spec

    def spec_hash(self) -> str | None:
        if not SPEC_CACHE_PATH.exists():
            return None
        return hashlib.sha256(SPEC_CACHE_PATH.read_bytes()).hexdigest()
