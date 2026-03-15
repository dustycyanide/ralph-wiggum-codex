#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-4.md"
EXPECTED_TEXT=$'# Queue Layer 4\n\nThis file confirms shared queue context was merged with item context.\n'
BUILDER_JSON="${RUN_DIR}/loop-01-iter-01-builder.json"
RESULT_JSON="${RUN_DIR}/result.json"

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected queue-layer-4 doc contents." >&2
  exit 1
fi

python3 - "${BUILDER_JSON}" "${RESULT_JSON}" <<'PY'
import json
import sys
from pathlib import Path

builder = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
result = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

if result.get("status") != "completed":
    raise SystemExit("Replay did not complete.")

context_files = builder.get("context_files_read") or []
skills = builder.get("skills_activated") or []

expected_context = ["specs/queue-layer-4.md", "ralph/codex_loop.py"]
if context_files != expected_context:
    raise SystemExit(f"Unexpected merged context read list: {context_files!r}")

if skills != ["09-implement-plan"]:
    raise SystemExit(f"Unexpected skills activated: {skills!r}")
PY
