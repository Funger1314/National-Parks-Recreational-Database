BEGIN;

TRUNCATE TABLE
    core.parking_area,
    core.trail,
    core.road,
    core.historic_site,
    core.facility,
    core.visitation,
    core.park
RESTART IDENTITY;

INSERT INTO metadata.source_dataset (
    dataset_key,
    dataset_name,
    source_agency,
    source_url,
    access_date_from_report,
    file_format,
    original_crs,
    stored_crs,
    expected_record_count,
    original_file_available,
    recovered_from_database,
    license_notes,
    limitations
)
VALUES
    ('np_visitation', 'Recovered visitation table', 'National Park Service', 'https://irma.nps.gov/STATS/', 'November and December 2022', 'CSV', NULL, NULL, 2064, FALSE, TRUE, 'Use NPS public dataset terms.', 'Recovered final merged table only.'),
    ('nps_boundary', 'Recovered NPS park boundary table', 'National Park Service', 'https://public-nps.opendata.arcgis.com/', 'November 2022', 'Shapefile', 'varied', 'ESRI:102003', 72, FALSE, TRUE, 'Use NPS public dataset terms.', 'Four invalid multipolygons remain in the legacy backup.'),
    ('nps_facilities', 'Recovered facility point table', 'USDA Forest Service', 'https://data.fs.usda.gov/geodata/edw/datasets.php?xmlKeyword=camp', 'December 2022', 'Shapefile', 'unknown', 'ESRI:102003', 21904, FALSE, TRUE, 'Use USDA public dataset terms.', 'Nationwide layer includes non-park context.'),
    ('nrhp_points', 'Recovered NRHP point table', 'National Park Service', 'https://www.nps.gov/subjects/nationalregister/database-research.htm', 'November 2022', 'Shapefile', 'unknown', 'ESRI:102003', 67443, FALSE, TRUE, 'Use NPS public dataset terms.', 'Nationwide layer extends beyond focal parks.'),
    ('park_roads', 'Recovered park roads table', 'National Park Service', 'https://public-nps.opendata.arcgis.com/', 'November 2022', 'Shapefile', 'varied', 'ESRI:102003', 4315, FALSE, TRUE, 'Use NPS public dataset terms.', 'Only four parks contain roads in the legacy project.'),
    ('park_trails', 'Recovered park trails table', 'National Park Service', 'https://public-nps.opendata.arcgis.com/', 'November 2022', 'Shapefile', 'varied', 'ESRI:102003', 1152, FALSE, TRUE, 'Use NPS public dataset terms.', 'Segment records do not equal unique trails.'),
    ('parking_areas', 'Recovered parking-area point table', 'National Park Service', 'https://public-nps.opendata.arcgis.com/', 'November 2022', 'Shapefile', 'varied', 'ESRI:102003', 872, FALSE, TRUE, 'Use NPS public dataset terms.', 'Only four parks contain parking coverage in the legacy project.')
ON CONFLICT (dataset_key) DO NOTHING;

INSERT INTO metadata.park_name_alias (raw_name, canonical_name, source_notes)
VALUES
    ('Rocky Mountain', 'Rocky Mountain', 'Recovered legacy canonical form.'),
    ('Rocky Mountain National Park', 'Rocky Mountain', 'Normalized modern alias.'),
    ('Great Smoky Mountain', 'Great Smoky Mountain', 'Recovered visitation and roads canonical form.'),
    ('Great Smoky Mountains', 'Great Smoky Mountain', 'Pluralized report wording.'),
    ('Great Smoky Mountains National Park', 'Great Smoky Mountain', 'Normalized modern alias.'),
    ('Grand Teton', 'Grand Teton', 'Recovered canonical form.'),
    ('Grand Teton National Park', 'Grand Teton', 'Normalized modern alias.'),
    ('Assateague Island', 'Assateague Island', 'Recovered visitation canonical form.'),
    ('Assateague Island National Seashore', 'Assateague Island', 'Normalized modern alias.')
ON CONFLICT (raw_name) DO NOTHING;

INSERT INTO core.park (
    canonical_name,
    state,
    unit_type,
    source_gid,
    area_square_meters,
    geometry,
    source_dataset_id
)
SELECT
    parkname,
    state,
    unit_type,
    gid,
    ST_Area(
        CASE
            WHEN ST_IsValid(geom) THEN geom
            ELSE ST_Multi(ST_CollectionExtract(ST_MakeValid(geom), 3))
        END
    ),
    CASE
        WHEN ST_IsValid(geom) THEN geom
        ELSE ST_Multi(ST_CollectionExtract(ST_MakeValid(geom), 3))
    END,
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'nps_boundary')
FROM legacy.nps_boundary;

INSERT INTO core.visitation (
    park_id,
    source_id,
    year,
    month_name,
    recreation_visitors,
    non_recreation_visitors,
    recreation_hr,
    non_recreation_hr,
    concession_lodging,
    tent_campers,
    rv_campers,
    concession_camping,
    backcountry_campers,
    misc_campers,
    non_recreation_overnight_stays,
    total_overnight_stays,
    source_dataset_id
)
SELECT
    p.park_id,
    v.id,
    v.year,
    v.month,
    v.recreation_visitors,
    v.non_recreation_visitors,
    v.recreation_hr,
    v.non_recreation_hr,
    v.concession_lodging,
    v.tent_campers,
    v.rv_campers,
    v.concession_camping,
    v.backcountry_campers,
    v.misc_campers,
    v.non_recreation_overnight_stays,
    v.total_overnight_stays,
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'np_visitation')
FROM legacy.np_visitation AS v
JOIN metadata.park_name_alias AS alias
    ON alias.raw_name = v.np_name
JOIN core.park AS p
    ON p.canonical_name = alias.canonical_name;

INSERT INTO core.road (
    park_id,
    source_gid,
    park_name_raw,
    road_name,
    road_surface,
    seasonal_flag,
    seasonal_description,
    source_length_meters,
    geometry,
    source_dataset_id
)
SELECT
    p.park_id,
    r.gid,
    r.park_name,
    r.road_name,
    r.rdsurface,
    r.seasonal,
    r.seasdesc,
    r.shape_length,
    ST_Force3DZ(r.geom),
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'park_roads')
FROM legacy.park_roads AS r
LEFT JOIN metadata.park_name_alias AS alias
    ON alias.raw_name = r.park_name
LEFT JOIN core.park AS p
    ON p.canonical_name = alias.canonical_name;

INSERT INTO core.trail (
    park_id,
    source_gid,
    park_name_raw,
    trail_name,
    trail_type,
    trail_use,
    historic_significance,
    source_length_meters,
    geometry,
    source_dataset_id
)
SELECT
    p.park_id,
    t.gid,
    t.park_name,
    t.trailname,
    t.trailtype,
    t.trluse,
    t.hist_signf,
    t.shape_leng,
    t.geom,
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'park_trails')
FROM legacy.park_trails AS t
LEFT JOIN metadata.park_name_alias AS alias
    ON alias.raw_name = t.park_name
LEFT JOIN core.park AS p
    ON p.canonical_name = alias.canonical_name;

INSERT INTO core.parking_area (
    park_id,
    source_gid,
    park_name_raw,
    lot_type,
    route_name,
    surface,
    total_space,
    handicapped_space,
    seasonal_flag,
    year_built,
    notes,
    geometry,
    source_dataset_id
)
SELECT
    p.park_id,
    a.gid,
    a.park_name,
    a.lottype,
    a.rte_name,
    a.surface,
    a.total_space,
    a.handicapped,
    a.seasonal,
    a.yearblt,
    a.notes,
    ST_Force3DZ(a.geom),
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'parking_areas')
FROM legacy.parking_areas AS a
LEFT JOIN metadata.park_name_alias AS alias
    ON alias.raw_name = a.park_name
LEFT JOIN core.park AS p
    ON p.canonical_name = alias.canonical_name;

INSERT INTO core.facility (
    park_id,
    source_gid,
    facility_type,
    notes,
    geometry,
    source_dataset_id
)
SELECT
    boundary_match.park_id,
    f.gid,
    f.facility_type,
    f.notes,
    f.geom,
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'nps_facilities')
FROM legacy.nps_facilities AS f
LEFT JOIN LATERAL (
    SELECT
        CASE
            WHEN COUNT(*) = 1 THEN MIN(p.park_id)
            ELSE NULL
        END AS park_id
    FROM core.park AS p
    WHERE ST_Contains(p.geometry, f.geom)
) AS boundary_match ON TRUE;

INSERT INTO core.historic_site (
    park_id,
    source_gid,
    nris_refnu,
    resource_name,
    resource_type,
    address,
    city,
    county,
    state,
    status,
    listed_date,
    geometry,
    source_dataset_id
)
SELECT
    boundary_match.park_id,
    h.gid,
    h.nris_refnu,
    h.resname,
    h.restype,
    h.address,
    h.city,
    h.county,
    h.state,
    h.status,
    h.listed_date,
    h.geom,
    (SELECT source_dataset_id FROM metadata.source_dataset WHERE dataset_key = 'nrhp_points')
FROM legacy.nrhp_points AS h
LEFT JOIN LATERAL (
    SELECT
        CASE
            WHEN COUNT(*) = 1 THEN MIN(p.park_id)
            ELSE NULL
        END AS park_id
    FROM core.park AS p
    WHERE ST_Contains(p.geometry, h.geom)
) AS boundary_match ON TRUE;

COMMIT;
