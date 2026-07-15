#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

require_command docker
require_command file
require_legacy_dump

mkdir -p outputs/quality_reports

DUMP_PATH="$(legacy_dump_host_path)"
TOC_OUTPUT="outputs/quality_reports/legacy_toc.txt"
FILE_OUTPUT="outputs/quality_reports/legacy_file_type.txt"

echo "Inspecting dump format with file..."
file "$DUMP_PATH" | tee "$FILE_OUTPUT"

echo "Listing dump contents with pg_restore inside the container..."
docker compose run --rm db bash -lc "pg_restore -l \"$LEGACY_DUMP_CONTAINER_PATH\"" > "$TOC_OUTPUT"

echo "Wrote:"
echo "  - $FILE_OUTPUT"
echo "  - $TOC_OUTPUT"

