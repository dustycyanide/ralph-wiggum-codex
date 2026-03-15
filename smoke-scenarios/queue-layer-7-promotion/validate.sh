#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-7.md"
EXPECTED_TEXT=$'# Queue Layer 7\n\nThis file confirms the planner promoted Q2 before building.\n'
PLANNER_JSON="${RUN_DIR}/loop-01-planner.json"
RESULT_JSON="${RUN_DIR}/result.json"

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected queue-layer-7 doc contents." >&2
  exit 1
fi

python3 - "${RUN_DIR}" "${PLANNER_JSON}" "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
planner = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
result = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

if planner.get("active_queue_id") != "Q2":
    raise SystemExit(f"Planner did not promote Q2: {planner}")

builder_files = sorted(run_dir.glob("loop-*-iter-*-builder.json"))
if not builder_files:
    raise SystemExit("Expected at least one builder response.")

for path in builder_files:
    builder = json.loads(path.read_text(encoding="utf-8"))
    if builder.get("active_queue_id") != "Q2":
        raise SystemExit(f"Builder executed from non-active queue: {builder}")

if result.get("status") not in {"completed", "incomplete"}:
    raise SystemExit(f"Unexpected replay result: {result}")
PY
