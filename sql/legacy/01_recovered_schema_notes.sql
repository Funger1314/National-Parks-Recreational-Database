-- Recovered schema notes from the legacy PostgreSQL/PostGIS backup.
--
-- Key observations:
-- 1. The dump is PostgreSQL custom format, not plain-text SQL.
-- 2. The recovered project tables live in the legacy database's public schema.
-- 3. The visitation table uses integer columns backed by owned sequences for many
--    ordinary measures because the original implementation modeled those columns as SERIAL.
-- 4. Geometry columns are declared with SRID 102003.
-- 5. The recovered dump contains GiST indexes for each spatial table.

