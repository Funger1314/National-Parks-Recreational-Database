# Reconstruction Notes

## What Was Recovered Directly

- the project report text, figures, and SQL examples
- the legacy PostgreSQL/PostGIS custom dump
- the final processed visitation table embedded in that dump
- the final spatial tables embedded in that dump

## What Was Reconstructed

- the executable Python ETL package
- shell scripts for restore, export, analysis, and quality checks
- corrected SQL queries
- the normalized `core` schema
- modernized documentation and tests

## What Was Improved

- explicit provenance tracking
- deterministic CSV export paths
- reproducible analysis outputs
- corrected count logic for Question 3
- documented CRS comparison between `ESRI:102003` and `EPSG:5070`
- clearer distinction between record counts and unique named features

## Assumptions

- the supplied dump is the authoritative recovered source for actual row counts and analytical outputs
- the report's screenshots are incomplete and therefore support, but do not fully define, the original notebook logic
- the four visitation park names should be standardized to `Rocky Mountain`, `Great Smoky Mountain`, `Grand Teton`, and `Assateague Island`

