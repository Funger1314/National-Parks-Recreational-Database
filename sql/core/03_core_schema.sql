CREATE TABLE IF NOT EXISTS core.park (
    park_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    state TEXT,
    unit_type TEXT,
    source_gid INTEGER,
    area_square_meters DOUBLE PRECISION,
    geometry geometry(MultiPolygon, 102003),
    source_dataset_id INTEGER
);

CREATE TABLE IF NOT EXISTS core.visitation (
    visitation_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    park_id INTEGER,
    source_id INTEGER,
    year SMALLINT NOT NULL,
    month_name TEXT NOT NULL,
    recreation_visitors INTEGER NOT NULL,
    non_recreation_visitors INTEGER NOT NULL,
    recreation_hr INTEGER NOT NULL,
    non_recreation_hr INTEGER NOT NULL,
    concession_lodging INTEGER NOT NULL,
    tent_campers INTEGER NOT NULL,
    rv_campers INTEGER NOT NULL,
    concession_camping INTEGER NOT NULL,
    backcountry_campers INTEGER NOT NULL,
    misc_campers INTEGER NOT NULL,
    non_recreation_overnight_stays TEXT,
    total_overnight_stays INTEGER NOT NULL,
    source_dataset_id INTEGER
);

CREATE TABLE IF NOT EXISTS core.facility (
    facility_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    park_id INTEGER,
    source_gid INTEGER,
    facility_type TEXT,
    notes TEXT,
    geometry geometry(Point, 102003),
    source_dataset_id INTEGER
);

CREATE TABLE IF NOT EXISTS core.historic_site (
    historic_site_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    park_id INTEGER,
    source_gid INTEGER,
    nris_refnu TEXT,
    resource_name TEXT,
    resource_type TEXT,
    address TEXT,
    city TEXT,
    county TEXT,
    state TEXT,
    status TEXT,
    listed_date DATE,
    geometry geometry(Point, 102003),
    source_dataset_id INTEGER
);

CREATE TABLE IF NOT EXISTS core.road (
    road_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    park_id INTEGER,
    source_gid INTEGER,
    park_name_raw TEXT,
    road_name TEXT,
    road_surface TEXT,
    seasonal_flag TEXT,
    seasonal_description TEXT,
    source_length_meters DOUBLE PRECISION,
    geometry geometry(MultiLineStringZ, 102003),
    source_dataset_id INTEGER
);

CREATE TABLE IF NOT EXISTS core.trail (
    trail_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    park_id INTEGER,
    source_gid INTEGER,
    park_name_raw TEXT,
    trail_name TEXT,
    trail_type TEXT,
    trail_use TEXT,
    historic_significance TEXT,
    source_length_meters DOUBLE PRECISION,
    geometry geometry(MultiLineString, 102003),
    source_dataset_id INTEGER
);

CREATE TABLE IF NOT EXISTS core.parking_area (
    parking_area_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    park_id INTEGER,
    source_gid INTEGER,
    park_name_raw TEXT,
    lot_type TEXT,
    route_name TEXT,
    surface TEXT,
    total_space INTEGER,
    handicapped_space INTEGER,
    seasonal_flag TEXT,
    year_built TEXT,
    notes TEXT,
    geometry geometry(PointZ, 102003),
    source_dataset_id INTEGER
);

