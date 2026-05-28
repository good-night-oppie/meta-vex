"""pytest plugin: writes structured test results to .harness/test-result.json.

Eliminates the text-scraping fragility documented in pitfall #15 of the
agent-hook-rnd-discipline skill (pytest -q output format changes across
versions; regex on "(\\d+) passed" breaks silently).

Usage: install via `pip install -e reporters/pytest/` or add to conftest.py:
    pytest_plugins = ["ionq_hooks_pytest"]

The orchestrator's test_runner.py reads the JSON output if present and falls
back to text-parse if absent, so this plugin is optional but strongly
recommended.

Output schema (.harness/test-result.json):
{
  "ts": "ISO-8601 UTC",
  "passed": int,
  "failed": int,
  "skipped": int,
  "xfailed": int,
  "xpassed": int,
  "errors": int,
  "duration_s": float,
  "exit_status": int,
  "failures": [{"nodeid": "...", "message": "..."}]
}
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path


def _project_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".harness").exists():
            return p
        if (p / ".git").exists():
            return p
    return start


def pytest_configure(config):
    config._ionq_hooks = {
        "started": time.time(),
        "passed": 0, "failed": 0, "skipped": 0,
        "xfailed": 0, "xpassed": 0, "errors": 0,
        "failures": [],
    }


def pytest_runtest_logreport(report):
    """Called for setup/call/teardown of each test."""
    cfg = getattr(report.session.config, "_ionq_hooks", None) if hasattr(report, "session") else None
    # report.session may not be on the report in some versions; pull from item context
    if cfg is None:
        return
    if report.when != "call" and not (report.failed and report.when in ("setup", "teardown")):
        return
    if report.passed:
        if report.when == "call":
            cfg["passed"] += 1
    elif report.failed:
        if report.when == "call":
            cfg["failed"] += 1
        else:
            cfg["errors"] += 1
        cfg["failures"].append({
            "nodeid": report.nodeid,
            "when": report.when,
            "message": str(report.longrepr)[:500] if report.longrepr else "",
        })
    elif report.skipped:
        if hasattr(report, "wasxfail"):
            cfg["xfailed"] += 1
        else:
            cfg["skipped"] += 1


def pytest_sessionstart(session):
    pytest_configure(session.config)


def pytest_sessionfinish(session, exitstatus):
    cfg = getattr(session.config, "_ionq_hooks", None)
    if not cfg:
        return
    duration = time.time() - cfg["started"]

    root = _project_root(Path(str(session.config.rootpath)))
    out_dir = root / ".harness"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "test-result.json"

    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "passed": cfg["passed"],
        "failed": cfg["failed"],
        "skipped": cfg["skipped"],
        "xfailed": cfg["xfailed"],
        "xpassed": cfg["xpassed"],
        "errors": cfg["errors"],
        "duration_s": round(duration, 3),
        "exit_status": int(exitstatus),
        "failures": cfg["failures"][:50],  # cap
    }
    out_file.write_text(json.dumps(payload, indent=2))
