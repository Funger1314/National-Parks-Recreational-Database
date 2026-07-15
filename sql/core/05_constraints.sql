ALTER TABLE core.park
    ADD CONSTRAINT uq_core_park_canonical_name UNIQUE (canonical_name);

ALTER TABLE core.park
    ADD CONSTRAINT fk_core_park_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

ALTER TABLE core.visitation
    ADD CONSTRAINT fk_core_visitation_park
        FOREIGN KEY (park_id) REFERENCES core.park (park_id);

ALTER TABLE core.visitation
    ADD CONSTRAINT fk_core_visitation_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

ALTER TABLE core.visitation
    ADD CONSTRAINT ck_core_visitation_year CHECK (year BETWEEN 1900 AND 2100);

ALTER TABLE core.visitation
    ADD CONSTRAINT uq_core_visitation_park_year_month UNIQUE (park_id, year, month_name);

ALTER TABLE core.facility
    ADD CONSTRAINT fk_core_facility_park
        FOREIGN KEY (park_id) REFERENCES core.park (park_id);

ALTER TABLE core.facility
    ADD CONSTRAINT fk_core_facility_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

ALTER TABLE core.historic_site
    ADD CONSTRAINT fk_core_historic_site_park
        FOREIGN KEY (park_id) REFERENCES core.park (park_id);

ALTER TABLE core.historic_site
    ADD CONSTRAINT fk_core_historic_site_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

ALTER TABLE core.road
    ADD CONSTRAINT fk_core_road_park
        FOREIGN KEY (park_id) REFERENCES core.park (park_id);

ALTER TABLE core.road
    ADD CONSTRAINT fk_core_road_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

ALTER TABLE core.trail
    ADD CONSTRAINT fk_core_trail_park
        FOREIGN KEY (park_id) REFERENCES core.park (park_id);

ALTER TABLE core.trail
    ADD CONSTRAINT fk_core_trail_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

ALTER TABLE core.parking_area
    ADD CONSTRAINT fk_core_parking_area_park
        FOREIGN KEY (park_id) REFERENCES core.park (park_id);

ALTER TABLE core.parking_area
    ADD CONSTRAINT fk_core_parking_area_source_dataset
        FOREIGN KEY (source_dataset_id) REFERENCES metadata.source_dataset (source_dataset_id);

