#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env. Start from '.env.example' before running this script." >&2
  exit 1
fi

set -a
source .env
set +a

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

legacy_dump_host_path() {
  printf '%s\n' "${PROJECT_ROOT}/database/legacy/${LEGACY_DUMP_FILENAME}"
}

require_legacy_dump() {
  local dump_path
  dump_path="$(legacy_dump_host_path)"
  if [[ ! -f "$dump_path" ]]; then
    echo "Legacy dump not found at $dump_path" >&2
    exit 1
  fi
}

