#!/usr/bin/env bash
# One-shot heartbeat snapshot — extracted from loop_driver for ad-hoc use.
set -euo pipefail
exec bash "$(dirname "${BASH_SOURCE[0]}")/loop_driver.sh"
