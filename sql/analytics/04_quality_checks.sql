-- Geometry type and SRID checks.
SELECT 'nps_boundary' AS table_name, COUNT(*) AS row_count, COUNT(*) FILTER (WHERE ST_IsValid(geom)) AS valid_count, COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)) AS invalid_count, COUNT(*) FILTER (WHERE ST_IsEmpty(geom)) AS empty_count, COUNT(*) FILTER (WHERE geom IS NULL) AS null_count, MIN(ST_SRID(geom)) AS min_srid, MAX(ST_SRID(geom)) AS max_srid
FROM legacy.nps_boundary
UNION ALL
SELECT 'nps_facilities', COUNT(*), COUNT(*) FILTER (WHERE ST_IsValid(geom)), COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)), COUNT(*) FILTER (WHERE ST_IsEmpty(geom)), COUNT(*) FILTER (WHERE geom IS NULL), MIN(ST_SRID(geom)), MAX(ST_SRID(geom))
FROM legacy.nps_facilities
UNION ALL
SELECT 'nrhp_points', COUNT(*), COUNT(*) FILTER (WHERE ST_IsValid(geom)), COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)), COUNT(*) FILTER (WHERE ST_IsEmpty(geom)), COUNT(*) FILTER (WHERE geom IS NULL), MIN(ST_SRID(geom)), MAX(ST_SRID(geom))
FROM legacy.nrhp_points
UNION ALL
SELECT 'park_roads', COUNT(*), COUNT(*) FILTER (WHERE ST_IsValid(geom)), COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)), COUNT(*) FILTER (WHERE ST_IsEmpty(geom)), COUNT(*) FILTER (WHERE geom IS NULL), MIN(ST_SRID(geom)), MAX(ST_SRID(geom))
FROM legacy.park_roads
UNION ALL
SELECT 'park_trails', COUNT(*), COUNT(*) FILTER (WHERE ST_IsValid(geom)), COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)), COUNT(*) FILTER (WHERE ST_IsEmpty(geom)), COUNT(*) FILTER (WHERE geom IS NULL), MIN(ST_SRID(geom)), MAX(ST_SRID(geom))
FROM legacy.park_trails
UNION ALL
SELECT 'parking_areas', COUNT(*), COUNT(*) FILTER (WHERE ST_IsValid(geom)), COUNT(*) FILTER (WHERE NOT ST_IsValid(geom)), COUNT(*) FILTER (WHERE ST_IsEmpty(geom)), COUNT(*) FILTER (WHERE geom IS NULL), MIN(ST_SRID(geom)), MAX(ST_SRID(geom))
FROM legacy.parking_areas
ORDER BY table_name;

-- Duplicate park-name check for visitation.
SELECT
    np_name,
    year,
    month,
    COUNT(*) AS duplicate_count
FROM legacy.np_visitation
GROUP BY np_name, year, month
HAVING COUNT(*) > 1;

