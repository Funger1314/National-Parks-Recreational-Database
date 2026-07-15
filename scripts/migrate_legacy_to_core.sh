#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

require_command docker
require_legacy_dump

echo "Running deterministic migration from legacy compatibility views into the core schema..."
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f /sql/core/06_migrate_from_legacy.sql

if [[ -x .venv/bin/python ]]; then
  echo "Generating migration reconciliation report from the recovered dump..."
  MPLCONFIGDIR="$PROJECT_ROOT/work/mplconfig" .venv/bin/python -m national_parks.cli reconcile-migration \
    --dump "$(legacy_dump_host_path)" \
    --output-path outputs/quality_reports/migration_reconciliation.csv
else
  echo "Skipping migration reconciliation report generation because .venv/bin/python is unavailable." >&2
fi

echo "Migration completed."
