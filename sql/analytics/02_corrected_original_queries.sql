-- Corrected analytical versions of the original report queries.

-- Q1
WITH colorado_parks AS (
    SELECT
        parkname,
        state,
        ST_Area(geom) AS area_square_meters
    FROM legacy.nps_boundary
    WHERE state = 'CO'
)
SELECT
    state,
    parkname,
    area_square_meters / 4046.8564224 AS area_acres,
    area_square_meters / 1000000.0 AS area_sq_km
FROM colorado_parks
ORDER BY parkname;

-- Q2
SELECT
    np_name,
    SUM(COALESCE(recreation_visitors, 0) + COALESCE(non_recreation_visitors, 0)) AS visitors_2010_2020
FROM legacy.np_visitation
WHERE year BETWEEN 2010 AND 2020
GROUP BY np_name
ORDER BY visitors_2010_2020 DESC, np_name;

-- Q3
WITH rocky AS (
    SELECT geom
    FROM legacy.nps_boundary
    WHERE parkname = 'Rocky Mountain'
),
campgrounds AS (
    SELECT COUNT(*) AS campground_records
    FROM legacy.nps_facilities AS f
    CROSS JOIN rocky
    WHERE f.facility_type = 'Campground'
      AND ST_Contains(rocky.geom, f.geom)
),
historic_sites AS (
    SELECT COUNT(*) AS nrhp_records
    FROM legacy.nrhp_points AS h
    CROSS JOIN rocky
    WHERE ST_Contains(rocky.geom, h.geom)
),
trail_stats AS (
    SELECT
        COUNT(*) AS trail_records,
        COUNT(DISTINCT NULLIF(trailname, '')) AS distinct_trail_names,
        COUNT(*) FILTER (WHERE NULLIF(trailname, '') IS NULL) AS unnamed_trail_records
    FROM legacy.park_trails
    WHERE park_name = 'Rocky Mountain'
),
parking_stats AS (
    SELECT COUNT(*) AS parking_records
    FROM legacy.parking_areas
    WHERE park_name = 'Rocky Mountain'
)
SELECT
    'Rocky Mountain' AS park_name,
    campgrounds.campground_records,
    historic_sites.nrhp_records,
    trail_stats.trail_records,
    trail_stats.distinct_trail_names,
    trail_stats.unnamed_trail_records,
    parking_stats.parking_records
FROM campgrounds
CROSS JOIN historic_sites
CROSS JOIN trail_stats
CROSS JOIN parking_stats;

-- Q4
WITH target_parks AS (
    SELECT parkname, geom
    FROM legacy.nps_boundary
    WHERE parkname IN ('Rocky Mountain', 'Great Smoky Mountain', 'Grand Teton')
),
unpaved_roads AS (
    SELECT *
    FROM legacy.park_roads
    WHERE rdsurface IN ('Native or Dirt', 'Gravel')
)
SELECT
    p.parkname,
    COUNT(*) FILTER (WHERE ST_Contains(p.geom, r.geom)) AS contains_count,
    SUM(r.shape_length) FILTER (WHERE ST_Contains(p.geom, r.geom)) / 1000.0 AS contains_length_km,
    COUNT(*) FILTER (WHERE ST_Intersects(p.geom, r.geom)) AS intersects_count,
    SUM(ST_Length(r.geom)) FILTER (WHERE ST_Intersects(p.geom, r.geom)) / 1000.0 AS intersects_geom_length_km,
    SUM(ST_Length(ST_Intersection(p.geom, r.geom))) FILTER (WHERE ST_Intersects(p.geom, r.geom)) / 1000.0 AS clipped_length_km
FROM target_parks AS p
JOIN unpaved_roads AS r
    ON ST_Intersects(p.geom, r.geom)
GROUP BY p.parkname
ORDER BY p.parkname;

-- Q5
WITH park_totals AS (
    SELECT
        np_name,
        SUM(COALESCE(recreation_visitors, 0) + COALESCE(non_recreation_visitors, 0)) AS total_visitation
    FROM legacy.np_visitation
    GROUP BY np_name
)
SELECT
    np_name,
    total_visitation,
    AVG(total_visitation) OVER () AS average_total_visitation
FROM park_totals
WHERE total_visitation > (SELECT AVG(total_visitation) FROM park_totals)
ORDER BY total_visitation DESC, np_name;

