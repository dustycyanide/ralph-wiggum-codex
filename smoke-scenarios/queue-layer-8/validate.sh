#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

PLAN_FILE="${ROOT_DIR}/IMPLEMENTATION_PLAN.md"
EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-8.md"
EXPECTED_TEXT=$'# Queue Layer 8\n\nThis file confirms runtime audit facts stayed out of the durable plan.\n'
BUILDER_JSON="${RUN_DIR}/loop-01-iter-01-builder.json"
RESULT_JSON="${RUN_DIR}/result.json"

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected queue-layer-8 doc contents." >&2
  exit 1
fi

for forbidden in "Planner Execution State" "Actual Context Files Read" "Actual Skills Activated" "Builder Contract Issues"; do
  if grep -q "${forbidden}" "${PLAN_FILE}"; then
    echo "Durable plan still contains runtime section: ${forbidden}" >&2
    exit 1
  fi
done

python3 - "${BUILDER_JSON}" "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

builder = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
result = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

if result.get("status") != "completed":
    raise SystemExit("Replay did not complete.")

if builder.get("context_files_read") != ["specs/queue-layer-8.md"]:
    raise SystemExit(
        f"Unexpected runtime context audit in builder JSON: {builder.get('context_files_read')!r}"
    )

if builder.get("skills_activated") != ["09-implement-plan"]:
    raise SystemExit(
        f"Unexpected runtime skill audit in builder JSON: {builder.get('skills_activated')!r}"
    )
PY
