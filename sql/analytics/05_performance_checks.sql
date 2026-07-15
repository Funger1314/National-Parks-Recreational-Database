-- Run these statements manually after restoring the legacy database and creating indexes.
-- Actual timings should be recorded in docs/performance.md only after execution.

EXPLAIN ANALYZE
SELECT
    b.parkname,
    COUNT(*)
FROM legacy.nps_boundary AS b
JOIN legacy.nrhp_points AS h
    ON ST_Contains(b.geom, h.geom)
WHERE b.parkname = 'Rocky Mountain'
GROUP BY b.parkname;

EXPLAIN ANALYZE
SELECT
    b.parkname,
    SUM(ST_Length(ST_Intersection(b.geom, r.geom)))
FROM legacy.nps_boundary AS b
JOIN legacy.park_roads AS r
    ON ST_Intersects(b.geom, r.geom)
WHERE b.parkname IN ('Rocky Mountain', 'Great Smoky Mountain', 'Grand Teton')
GROUP BY b.parkname;

