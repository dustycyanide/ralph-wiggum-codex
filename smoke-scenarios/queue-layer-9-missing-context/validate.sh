#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"
RUN_DIR="${2:?run dir required}"

PLAN_FILE="${ROOT_DIR}/IMPLEMENTATION_PLAN.md"
RESULT_JSON="${RUN_DIR}/result.json"
BUILDER_JSON="${RUN_DIR}/loop-01-iter-01-builder.json"
ISSUES_FILE="${RUN_DIR}/builder-issues.jsonl"

if [[ -f "${ROOT_DIR}/docs/queue-layer-9.md" ]]; then
  echo "Builder should not have created docs/queue-layer-9.md." >&2
  exit 1
fi

if [[ ! -f "${ISSUES_FILE}" ]]; then
  echo "Expected builder-issues.jsonl to exist." >&2
  exit 1
fi

if ! grep -q ".queue-layer-9-required.md" "${PLAN_FILE}"; then
  echo "Planner did not keep missing context in durable blocker metadata." >&2
  exit 1
fi

python3 - "${BUILDER_JSON}" "${RESULT_JSON}" "${ISSUES_FILE}" <<'PY'
import json
import sys
from pathlib import Path

builder = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
result = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
issues = [json.loads(line) for line in Path(sys.argv[3]).read_text(encoding="utf-8").splitlines() if line]

if builder.get("status") != "blocked":
    raise SystemExit(f"Builder did not block: {builder}")

if builder.get("issue_type") not in {
    "contract",
    "contract_invalid",
    "contract_issue",
    "missing_required_context",
}:
    raise SystemExit(f"Unexpected builder issue type: {builder}")

if not any(".queue-layer-9-required.md" in (issue.get("issue_detail") or "") for issue in issues):
    raise SystemExit(f"Missing context issue was not logged: {issues!r}")

if result.get("status") not in {"waiting", "incomplete"}:
    raise SystemExit(f"Unexpected replay result: {result}")
PY
