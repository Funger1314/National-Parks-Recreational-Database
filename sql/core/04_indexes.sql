CREATE INDEX IF NOT EXISTS idx_core_park_canonical_name ON core.park (canonical_name);
CREATE INDEX IF NOT EXISTS idx_core_park_geometry ON core.park USING GIST (geometry);

CREATE INDEX IF NOT EXISTS idx_core_visitation_park_year ON core.visitation (park_id, year);
CREATE INDEX IF NOT EXISTS idx_core_facility_park_id ON core.facility (park_id);
CREATE INDEX IF NOT EXISTS idx_core_facility_geometry ON core.facility USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_core_historic_site_park_id ON core.historic_site (park_id);
CREATE INDEX IF NOT EXISTS idx_core_historic_site_geometry ON core.historic_site USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_core_road_park_id ON core.road (park_id);
CREATE INDEX IF NOT EXISTS idx_core_road_geometry ON core.road USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_core_trail_park_id ON core.trail (park_id);
CREATE INDEX IF NOT EXISTS idx_core_trail_geometry ON core.trail USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_core_parking_area_park_id ON core.parking_area (park_id);
CREATE INDEX IF NOT EXISTS idx_core_parking_area_geometry ON core.parking_area USING GIST (geometry);

