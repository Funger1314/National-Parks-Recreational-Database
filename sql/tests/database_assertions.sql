-- Expected legacy row counts verified from the recovered backup.
SELECT 'np_visitation' AS table_name, COUNT(*) = 2064 AS row_count_matches FROM legacy.np_visitation;
SELECT 'nps_boundary' AS table_name, COUNT(*) = 72 AS row_count_matches FROM legacy.nps_boundary;
SELECT 'nps_facilities' AS table_name, COUNT(*) = 21904 AS row_count_matches FROM legacy.nps_facilities;
SELECT 'nrhp_points' AS table_name, COUNT(*) = 67443 AS row_count_matches FROM legacy.nrhp_points;
SELECT 'park_roads' AS table_name, COUNT(*) = 4315 AS row_count_matches FROM legacy.park_roads;
SELECT 'park_trails' AS table_name, COUNT(*) = 1152 AS row_count_matches FROM legacy.park_trails;
SELECT 'parking_areas' AS table_name, COUNT(*) = 872 AS row_count_matches FROM legacy.parking_areas;
