#!/usr/bin/env bash
set -euo pipefail

planner_json="${1:?planner json path required}"

while [ ! -f "$planner_json" ]; do
  sleep 0.1
done

perl -0pi -e 's/- Status: todo/- Status: done/' IMPLEMENTATION_PLAN.md
