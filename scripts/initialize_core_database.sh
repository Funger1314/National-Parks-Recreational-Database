#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/_common.sh"

require_command docker

echo "Ensuring database container is running..."
docker compose up -d db

for sql_file in \
  sql/core/00_extensions.sql \
  sql/core/01_schemas.sql \
  sql/core/02_metadata_tables.sql \
  sql/core/03_core_schema.sql \
  sql/core/04_indexes.sql \
  sql/core/05_constraints.sql; do
  echo "Applying $sql_file"
  docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f "/sql/${sql_file#sql/}"
done

echo "Creating compatibility views under the legacy schema..."
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<'SQL'
CREATE SCHEMA IF NOT EXISTS legacy;
CREATE OR REPLACE VIEW legacy.np_visitation AS SELECT * FROM public.np_visitation;
CREATE OR REPLACE VIEW legacy.nps_boundary AS SELECT * FROM public.nps_boundary;
CREATE OR REPLACE VIEW legacy.nps_facilities AS SELECT * FROM public.nps_facilities;
CREATE OR REPLACE VIEW legacy.nrhp_points AS SELECT * FROM public.nrhp_points;
CREATE OR REPLACE VIEW legacy.park_roads AS SELECT * FROM public.park_roads;
CREATE OR REPLACE VIEW legacy.park_trails AS SELECT * FROM public.park_trails;
CREATE OR REPLACE VIEW legacy.parking_areas AS SELECT * FROM public.parking_areas;
SQL

echo "Core database initialization completed."

