"""Smoke tests — no network, no coach MCP."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agentdex.main import app
from agentdex.swarm.hub import Hub, LeafTask
from agentdex.swarm.leaf import count_endpoints, list_schema_names


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root_identity() -> None:
    client = TestClient(app)
    resp = client.get("/")
    body = resp.json()
    assert body["name"] == "agentdex"
    assert body["lane"] == "showcase-dogfood"


@pytest.mark.asyncio
async def test_hub_fanout_uses_single_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_spec = {
        "paths": {"/a": {"get": {}, "post": {}}, "/b": {"get": {}}},
        "components": {"schemas": {"Foo": {}, "Bar": {}}},
    }
    fetch_count = {"n": 0}

    class FakeCache:
        async def fetch_spec(self, *, force: bool = False) -> dict:  # type: ignore[no-untyped-def]
            fetch_count["n"] += 1
            return fake_spec

    hub = Hub(cache=FakeCache())  # type: ignore[arg-type]
    tasks = [
        LeafTask("endpoints", ["paths"], count_endpoints),
        LeafTask("schemas", ["components"], list_schema_names),
    ]
    results = await hub.run(tasks)

    assert fetch_count["n"] == 1, "hub must fetch spec exactly once across N leaves"
    assert results["endpoints"].ok and results["endpoints"].value == 3
    assert results["schemas"].ok and results["schemas"].value == ["Bar", "Foo"]
