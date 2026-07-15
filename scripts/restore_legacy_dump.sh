#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

require_command docker
require_legacy_dump

if [[ "${ALLOW_PUBLIC_REPLACE:-0}" != "1" ]]; then
  echo "Refusing to replace existing public tables without ALLOW_PUBLIC_REPLACE=1." >&2
  echo "Set ALLOW_PUBLIC_REPLACE=1 when you intentionally want to rerun the legacy restore." >&2
  exit 1
fi

mkdir -p work outputs/quality_reports
TOC_FILE="work/legacy_restore.toc"
FILTERED_TOC_FILE="work/legacy_restore.filtered.toc"
MOUNTED_TOC_FILE="/workspace/outputs/legacy_restore.filtered.toc"

echo "Starting database container..."
docker compose up -d db

echo "Creating a filtered table-of-contents list for restore..."
docker compose run --rm db bash -lc "pg_restore -l \"$LEGACY_DUMP_CONTAINER_PATH\"" > "$TOC_FILE"
cp "$TOC_FILE" "$FILTERED_TOC_FILE"

IFS=',' read -r -a EXTENSIONS <<< "${LEGACY_SKIP_EXTENSIONS}"
for extension_name in "${EXTENSIONS[@]}"; do
  if [[ -n "$extension_name" ]]; then
    grep -v "$extension_name" "$FILTERED_TOC_FILE" > "${FILTERED_TOC_FILE}.tmp"
    mv "${FILTERED_TOC_FILE}.tmp" "$FILTERED_TOC_FILE"
  fi
done

cp "$FILTERED_TOC_FILE" outputs/legacy_restore.filtered.toc

echo "Restoring the legacy dump into the public schema..."
docker compose exec -T db bash -lc "
  pg_restore \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    --use-list=\"$MOUNTED_TOC_FILE\" \
    --dbname=\"$POSTGRES_DB\" \
    \"$LEGACY_DUMP_CONTAINER_PATH\"
" || {
  echo "Legacy restore failed. Review unsupported extensions and the filtered TOC list." >&2
  exit 1
}

echo "Legacy restore completed."
