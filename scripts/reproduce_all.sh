#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

./scripts/export_recovered_data.sh
./scripts/run_analysis.sh

if command -v docker >/dev/null 2>&1; then
  echo "Docker detected. Database workflow is available through:"
  echo "  ALLOW_PUBLIC_REPLACE=1 ./scripts/restore_legacy_dump.sh"
  echo "  ./scripts/initialize_core_database.sh"
  echo "  ./scripts/migrate_legacy_to_core.sh"
else
  echo "Docker is not available locally, so containerized restore steps were not executed."
fi

