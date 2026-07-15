#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

require_command docker

mkdir -p outputs/quality_reports

echo "Running SQL quality checks..."
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f /sql/analytics/04_quality_checks.sql

echo "Quality checks completed."

