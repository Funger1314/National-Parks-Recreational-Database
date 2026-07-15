-- Seasonality
SELECT
    np_name,
    month,
    AVG(recreation_visitors + non_recreation_visitors) AS avg_monthly_visitors
FROM legacy.np_visitation
GROUP BY np_name, month
ORDER BY np_name, month;

-- Visitation pressure proxy using average annual visitation from 2010-2020.
WITH annual_visits AS (
    SELECT
        np_name,
        year,
        SUM(recreation_visitors + non_recreation_visitors) AS total_visitors
    FROM legacy.np_visitation
    WHERE year BETWEEN 2010 AND 2020
    GROUP BY np_name, year
),
park_area AS (
    SELECT
        parkname,
        ST_Area(geom) / 1000000.0 AS area_sq_km
    FROM legacy.nps_boundary
    WHERE parkname IN ('Rocky Mountain', 'Great Smoky Mountain', 'Grand Teton', 'Assateague Island')
)
SELECT
    a.np_name,
    AVG(a.total_visitors) AS avg_annual_visitors,
    p.area_sq_km,
    AVG(a.total_visitors) / p.area_sq_km AS avg_annual_visitors_per_sq_km
FROM annual_visits AS a
JOIN park_area AS p
    ON p.parkname = a.np_name
GROUP BY a.np_name, p.area_sq_km
ORDER BY avg_annual_visitors_per_sq_km DESC;

-- Infrastructure density by park.
WITH park_area AS (
    SELECT
        parkname,
        ST_Area(geom) / 1000000.0 AS area_sq_km
    FROM legacy.nps_boundary
    WHERE parkname IN ('Rocky Mountain', 'Great Smoky Mountain', 'Grand Teton', 'Assateague Island')
)
SELECT
    p.parkname,
    SUM(r.shape_length) / 1000.0 / p.area_sq_km * 100.0 AS road_km_per_100_sq_km,
    (
        SELECT SUM(t.shape_leng) / 1000.0
        FROM legacy.park_trails AS t
        WHERE t.park_name = p.parkname
    ) / p.area_sq_km * 100.0 AS trail_km_per_100_sq_km,
    (
        SELECT COUNT(*)
        FROM legacy.parking_areas AS a
        WHERE a.park_name = p.parkname
    ) / p.area_sq_km * 100.0 AS parking_records_per_100_sq_km
FROM park_area AS p
JOIN legacy.park_roads AS r
    ON r.park_name = p.parkname
GROUP BY p.parkname, p.area_sq_km
ORDER BY p.parkname;

-- Data completeness matrix for the four focal parks.
SELECT
    park.parkname,
    EXISTS (SELECT 1 FROM legacy.np_visitation AS v WHERE v.np_name = park.parkname) AS has_visitation,
    EXISTS (SELECT 1 FROM legacy.park_roads AS r WHERE r.park_name = park.parkname) AS has_roads,
    EXISTS (SELECT 1 FROM legacy.park_trails AS t WHERE t.park_name = park.parkname) AS has_trails,
    EXISTS (SELECT 1 FROM legacy.parking_areas AS a WHERE a.park_name = park.parkname) AS has_parking,
    EXISTS (
        SELECT 1
        FROM legacy.nps_facilities AS f
        WHERE ST_Contains(park.geom, f.geom)
    ) AS has_facilities,
    EXISTS (
        SELECT 1
        FROM legacy.nrhp_points AS h
        WHERE ST_Contains(park.geom, h.geom)
    ) AS has_historic_sites,
    TRUE AS has_boundary
FROM legacy.nps_boundary AS park
WHERE park.parkname IN ('Rocky Mountain', 'Great Smoky Mountain', 'Grand Teton', 'Assateague Island')
ORDER BY park.parkname;

