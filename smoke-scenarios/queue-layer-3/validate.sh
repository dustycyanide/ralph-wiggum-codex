#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

EXPECTED_DOC="${ROOT_DIR}/docs/queue-layer-3.md"
EXPECTED_TEXT=$'# Queue Layer 3\n\nThis file confirms required context was read and conditional context stayed deferred.\n'
BUILDER_JSON="${RUN_DIR}/loop-01-iter-01-builder.json"
RESULT_JSON="${RUN_DIR}/result.json"

if [[ ! -f "${EXPECTED_DOC}" ]]; then
  echo "Missing expected doc: ${EXPECTED_DOC}" >&2
  exit 1
fi

if [[ "$(cat "${EXPECTED_DOC}")"$'\n' != "${EXPECTED_TEXT}" ]]; then
  echo "Unexpected queue-layer-3 doc contents." >&2
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

expected_context = ["IMPLEMENTATION_PLAN.md", "specs/queue-layer-3.md"]
if context_files != expected_context:
    raise SystemExit(f"Unexpected context read list: {context_files!r}")

if "docs/ralph-research.md" in context_files:
    raise SystemExit("Conditional context should have stayed deferred.")

if any("/.codex/skills/" in path for path in context_files):
    raise SystemExit(f"Skill files leaked into context_files_read: {context_files!r}")

if skills != ["09-implement-plan"]:
    raise SystemExit(f"Unexpected skills activated: {skills!r}")
PY
