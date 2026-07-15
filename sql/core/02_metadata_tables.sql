CREATE TABLE IF NOT EXISTS metadata.source_dataset (
    source_dataset_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_key TEXT NOT NULL UNIQUE,
    dataset_name TEXT NOT NULL,
    source_agency TEXT NOT NULL,
    source_url TEXT,
    access_date_from_report TEXT,
    file_format TEXT,
    original_crs TEXT,
    stored_crs TEXT,
    expected_record_count INTEGER,
    original_file_available BOOLEAN NOT NULL DEFAULT FALSE,
    recovered_from_database BOOLEAN NOT NULL DEFAULT TRUE,
    license_notes TEXT,
    limitations TEXT
);

CREATE TABLE IF NOT EXISTS metadata.park_name_alias (
    park_name_alias_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raw_name TEXT NOT NULL UNIQUE,
    canonical_name TEXT NOT NULL,
    source_notes TEXT
);

