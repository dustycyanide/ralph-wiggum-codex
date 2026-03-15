#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-2.md"
EXPECTED_TEXT=$'# Queue Layer 2\n\nThis file confirms the builder respected structured context and skill descriptors.\n'
BUILDER_JSON="${RUN_DIR}/loop-01-iter-01-builder.json"
RESULT_JSON="${RUN_DIR}/result.json"

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected queue-layer-2 doc contents." >&2
  exit 1
fi

python3 - "${BUILDER_JSON}" "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

builder_path = Path(sys.argv[1])
result_path = Path(sys.argv[2])

builder = json.loads(builder_path.read_text(encoding="utf-8"))
result = json.loads(result_path.read_text(encoding="utf-8"))

if result.get("status") != "completed":
    raise SystemExit("Replay did not complete.")

context_files = set(builder.get("context_files_read") or [])
skills = set(builder.get("skills_activated") or [])

required_context = {"IMPLEMENTATION_PLAN.md", "specs/queue-layer-2.md"}
if not required_context.issubset(context_files):
    raise SystemExit(
        f"Missing required context files. saw={sorted(context_files)}"
    )

if "09-implement-plan" not in skills:
    raise SystemExit(f"Missing required skill activation. saw={sorted(skills)}")
PY
