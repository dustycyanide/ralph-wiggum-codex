#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

PLAN_FILE="${ROOT_DIR}/IMPLEMENTATION_PLAN.md"
RESULT_JSON="${RUN_DIR}/result.json"

if [[ -f "${RUN_DIR}/loop-01-iter-01-builder.json" ]]; then
  echo "Builder should not have run for strict external input scenario." >&2
  exit 1
fi

if grep -q "Planner Decision: optimistic" "${PLAN_FILE}"; then
  echo "External input scenario should not be marked optimistic." >&2
  exit 1
fi

python3 - "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if result.get("status") != "waiting":
    raise SystemExit(f"Unexpected replay result: {result}")
PY
