#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

PLAN_FILE="${ROOT_DIR}/IMPLEMENTATION_PLAN.md"
RESULT_JSON="${RUN_DIR}/result.json"
EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-5-optimistic.md"
EXPECTED_TEXT=$'# Queue Layer 5 Optimistic\n\nThis file confirms the planner proceeded optimistically on sequencing-only work.\n'

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected optimistic doc contents." >&2
  exit 1
fi

if [[ "$(grep -c "Planner Decision: optimistic" "${PLAN_FILE}")" -lt 2 ]]; then
  echo "Expected optimistic planner decisions for queue and item." >&2
  exit 1
fi

python3 - "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if result.get("status") != "completed":
    raise SystemExit(f"Unexpected replay result: {result}")
PY
