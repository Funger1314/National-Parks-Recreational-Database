# Database Notes

The repository uses a dual-track database design:

- `legacy` preserves the recovered 2022 PostgreSQL/PostGIS structures as closely as possible.
- `core`, `analytics`, and `metadata` contain the modernized schema and derived outputs.

## Source Dump Placement

Place the original PostgreSQL custom-format dump at:

`database/legacy/NP_Database_postgres_Group1.dump`

The file is intentionally not committed to the repository.

## Container Workflow

```bash
cp .env.example .env
docker compose up -d
make inspect
make restore-legacy
make initialize-core
make migrate
```

## Extension Caveat

The recovered dump references optional extensions such as `ogr_fdw`, `pgrouting`,
`pointcloud`, and `pointcloud_postgis`. The default `postgis/postgis` image does not
ship every one of these extensions. The restore scripts therefore support filtering
unsupported extension entries so the project tables can still be restored reproducibly.

