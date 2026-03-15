#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

PLAN_FILE="${ROOT_DIR}/IMPLEMENTATION_PLAN.md"
EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-6-a.md"
RESULT_JSON="${RUN_DIR}/result.json"
EXPECTED_TEXT=$'# Queue Layer 6 A\n\nThis file confirms unlock metadata reordered the queue.\n'

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ -f "${ROOT_DIR}/docs/queue-layer-6-b.md" ]]; then
  echo "Dependent doc should not be created in the first pass." >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected reorder doc contents." >&2
  exit 1
fi

python3 - "${PLAN_FILE}" "${RESULT_JSON}" <<'PY'
import json
import re
import sys
from pathlib import Path

plan_text = Path(sys.argv[1]).read_text(encoding="utf-8")
result = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

titles = re.findall(r"#### T\d+\n- Status: .*?\n- Title: (.+)", plan_text)
if titles[:2] != ["Create `docs/queue-layer-6-a.md`", "Create `docs/queue-layer-6-b.md`"]:
    raise SystemExit(f"Unexpected todo order: {titles!r}")

if result.get("status") not in {"waiting", "incomplete"}:
    raise SystemExit(f"Unexpected replay result: {result}")
PY
