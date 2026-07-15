-- Reconstructed from the original December 2022 report.
-- These queries preserve the report's wording and known issues and are intentionally
-- not silently corrected here.

-- Question 1
SELECT
    state,
    parkname,
    SUM(ST_Area(geom)) / 4047 AS park_acres
FROM legacy.nps_boundary
WHERE state = 'CO'
GROUP BY parkname, state;

-- Question 2
SELECT
    np_name,
    SUM(recreation_visitors + non_recreation_visitors) AS visitors
FROM legacy.np_visitation
WHERE year BETWEEN 2010 AND 2020
GROUP BY np_name;

-- Question 3
SELECT
    nb.parkname,
    COUNT(*) AS campground_num,
    nrhp.nrhp_sites AS nrhp_num,
    trail_number.trails AS trail_num,
    parkinglot.parking AS pk_lot_num
FROM legacy.nps_boundary AS nb
JOIN legacy.nps_facilities AS nf ON ST_Contains(nb.geom, nf.geom),
(
    SELECT COUNT(*) AS nrhp_sites
    FROM legacy.nps_boundary AS b
    JOIN legacy.nps_facilities AS f ON ST_Contains(b.geom, f.geom)
    JOIN legacy.nrhp_points AS n ON ST_Contains(b.geom, n.geom)
    WHERE b.parkname = 'Rocky Mountain' AND f.facility_type = 'Campground'
) AS nrhp,
(
    SELECT COUNT(*) AS trails
    FROM legacy.park_trails
    WHERE park_name = 'Rocky Mountain'
) AS trail_number,
(
    SELECT COUNT(*) AS parking
    FROM legacy.parking_areas
    WHERE park_name = 'Rocky Mountain'
) AS parkinglot
WHERE nb.parkname = 'Rocky Mountain'
  AND nf.facility_type = 'Campground'
GROUP BY nb.parkname, nrhp_num, trail_num, pk_lot_num;

-- Question 4
SELECT
    b.parkname,
    COUNT(*) AS road_num,
    SUM(r.shape_length) / 1000 AS rd_length_km
FROM legacy.park_roads AS r,
     legacy.nps_boundary AS b
WHERE ST_Contains(b.geom, r.geom)
  AND b.parkname IN ('Rocky Mountain', 'Great Smoky Mountain', 'Grand Teton')
  AND r.rdsurface IN ('Native or Dirt', 'Gravel')
GROUP BY b.parkname;

-- Question 5
SELECT
    np_name,
    SUM(recreation_visitors + non_recreation_visitors) AS visitors
FROM legacy.np_visitation
GROUP BY np_name
HAVING SUM(recreation_visitors + non_recreation_visitors) > (
    SELECT AVG(s.total_visitation)
    FROM (
        SELECT
            np_name,
            SUM(recreation_visitors + non_recreation_visitors) AS total_visitation
        FROM legacy.np_visitation
        GROUP BY np_name
    ) AS s
);

