#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

PLAN_FILE="${ROOT_DIR}/IMPLEMENTATION_PLAN.md"
EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-10.md"
EXPECTED_TEXT=$'# Queue Layer 10\n\nThis file confirms the feature wrapper stayed above queue-item execution.\n'
RESULT_JSON="${RUN_DIR}/result.json"
PLANNER_JSON="${RUN_DIR}/loop-01-planner.json"
BUILDER_JSON="${RUN_DIR}/loop-01-iter-01-builder.json"

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected queue-layer-10 doc contents." >&2
  exit 1
fi

if ! grep -q "### F1" "${PLAN_FILE}" || ! grep -q "Queues: Q1, Q2" "${PLAN_FILE}" || ! grep -q -- "- Status: completed" "${PLAN_FILE}"; then
  echo "Feature metadata did not remain durable/completed." >&2
  exit 1
fi

python3 - "${PLANNER_JSON}" "${BUILDER_JSON}" "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

planner = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
builder = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
result = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

if planner.get("active_queue_id") != "Q2":
    raise SystemExit(f"Planner did not target Q2 under F1: {planner}")

if builder.get("active_queue_id") != "Q2":
    raise SystemExit(f"Builder did not stay at queue granularity: {builder}")

if result.get("status") != "completed":
    raise SystemExit(f"Unexpected replay result: {result}")
PY
