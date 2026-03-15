#!/usr/bin/env bash
set -euo pipefail

planner_json="${1:?planner json path required}"
root_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

while [[ ! -f "${planner_json}" ]]; do
  sleep 0.2
done

rm -f "${root_dir}/.queue-layer-9-required.md"
