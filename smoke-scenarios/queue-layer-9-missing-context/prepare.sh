#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:?root dir required}"

cat > "${ROOT_DIR}/.queue-layer-9-required.md" <<'EOF'
# Queue Layer 9 Required Context

This file exists during planning and is removed before the builder starts.
EOF
