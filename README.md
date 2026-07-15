# National Parks Recreational Database Project

Spatial database and analytics workflow for comparing visitation, roads, trails, parking, facilities, and historic sites across selected U.S. national parks.

## Project Overview

This repository builds a reproducible geospatial data workflow that:

- ingests and exports park-related source tables
- organizes them in PostgreSQL/PostGIS
- normalizes parks, visitation, roads, trails, parking areas, facilities, and historic sites
- runs analytical SQL for the core project questions
- validates geometry quality and migration completeness
- generates figures, query outputs, and quality reports

The repository focuses on reproducible spatial analysis and database engineering rather than operational park management.

## Project Goals

The project helps users compare visitation pressure, transportation access, amenities, and historic resources across selected U.S. national parks.

## Research Questions

1. Which national parks are in Colorado, and what is the area of each park?
2. What was the total visitation of each national park from 2010 through 2020?
3. How many campgrounds, historical sites, trail records, and parking areas are in Rocky Mountain National Park?
4. How many unpaved road records are in Rocky Mountain, Great Smoky Mountain, and Grand Teton National Parks, and what are their total lengths?
5. Which national park has total visitation above the average total visitation of the four parks?

## Technology Stack

- Python
- Pandas
- PostgreSQL
- PostGIS
- Shapely
- PyProj
- Matplotlib
- Docker Compose
- pytest
- Ruff

## Source Datasets

- National Park Service visitation CSV exports
- NPS park boundaries
- NPS roads
- NPS trails
- NPS parking areas
- National Register of Historic Places points
- USDA Forest Service recreational facilities

See [data/source_manifest.yml](data/source_manifest.yml) and [docs/data_provenance.md](docs/data_provenance.md).

## Database Architecture

- `public.*` stores source tables imported from the database backup.
- `legacy.*` compatibility views provide a stable namespace for modern SQL.
- `core.*` stores normalized park, visitation, amenity, road, trail, parking, and historic-site records.
- `analytics.*` stores derived views and query logic.
- `metadata.*` records aliases and dataset provenance.

See [docs/architecture.md](docs/architecture.md) and [figures/diagrams/database_architecture.mmd](figures/diagrams/database_architecture.mmd).

## Quick Start

```bash
cp .env.example .env
make setup
make export-recovered
make analysis
```

If Docker is available and you want the database workflow as well:

```bash
docker compose up -d
make inspect
ALLOW_PUBLIC_REPLACE=1 make restore-legacy
make initialize-core
make migrate
make quality
```

## Repository Structure

- `src/national_parks/`: Python package for ETL, data export, provenance, and analysis.
- `sql/legacy/`: source-era schema notes and baseline SQL.
- `sql/core/`: modernized schema and migration SQL.
- `sql/analytics/`: corrected research-question queries, advanced analyses, and quality checks.
- `scripts/`: reproducibility entry points.
- `docs/`: audit, methodology, design, provenance, and limitations.
- `outputs/`: generated query results, quality reports, and figures.

## Selected Verified Findings

- The source tables contain 2,064 visitation rows, 72 park boundaries, 21,904 facilities, 67,443 historical-site points, 4,315 road records, 1,152 trail records, and 872 parking-area records.
- The four visitation parks each contain 516 monthly rows covering 1979 through 2021.
- Total visitation from 2010 through 2020 is highest for Great Smoky Mountain at 237,633,203 visits among the four-park subset.
- Great Smoky Mountain is the only park above the four-park average total visitation threshold in the analyzed dataset.
- Four `nps_boundary` geometries are invalid in the legacy backup; the legacy layer preserves them and the modern `core.park` migration repairs them.
- The stored CRS is `ESRI:102003`, and it is not equivalent to `EPSG:5070`.

See [docs/source_audit.md](docs/source_audit.md), [docs/query_results.md](docs/query_results.md), and [docs/methodology.md](docs/methodology.md).

## Database Import

The database import starts from a PostgreSQL custom-format backup produced by PostgreSQL 10.22. The default container workflow uses a current PostGIS image for practical restoration, and unsupported optional extensions referenced in the dump can be filtered during restore. See [database/README.md](database/README.md).

## Python ETL

Two workflows are supported:

- Workflow A: process raw visitation CSV files from `data/raw/visitation/`
- Workflow B: export the `np_visitation` table from the database backup into `data/recovered/np_visitation_recovered.csv`

Workflow B exports the already-processed final table and does not recreate every raw-data transformation step.

## Original SQL Questions

The original report queries are preserved in [sql/legacy/02_original_report_queries.sql](sql/legacy/02_original_report_queries.sql). Known issues are intentionally left intact there for historical transparency.

## Corrected SQL Queries

Corrected versions live in [sql/analytics/02_corrected_original_queries.sql](sql/analytics/02_corrected_original_queries.sql). The modernized queries:

- avoid `SERIAL` misuse for ordinary measures
- prevent count inflation in Question 3
- distinguish record counts from unique named features
- compare `ST_Contains`, `ST_Intersects`, and clipped-length approaches for roads
- use explicit metric and converted units

## Advanced Analyses

The repository includes analyses for:

- visitation seasonality
- visitation pressure per square kilometer
- infrastructure density
- data completeness
- historic-site density where supported

See [sql/analytics/03_advanced_analysis.sql](sql/analytics/03_advanced_analysis.sql).

## Data Quality Results

Generated outputs are written to:

- `outputs/query_results/`
- `outputs/quality_reports/`
- `outputs/figures/`

The spatial summary CSV is [outputs/quality_reports/spatial_quality_summary.csv](outputs/quality_reports/spatial_quality_summary.csv).
The migration acceptance report is [outputs/quality_reports/migration_reconciliation.csv](outputs/quality_reports/migration_reconciliation.csv).

## Spatial Query Methodology

The modern analysis documents geometry type, SRID, validity, containment-versus-intersection tradeoffs, and unit conversions. See [docs/methodology.md](docs/methodology.md).

## Performance Notes

Performance-check SQL is prepared in [sql/analytics/05_performance_checks.sql](sql/analytics/05_performance_checks.sql). Actual `EXPLAIN ANALYZE` timings should be recorded only after running them in a live PostGIS environment.

## Limitations

See [docs/limitations.md](docs/limitations.md) and [docs/reconstruction_notes.md](docs/reconstruction_notes.md).

## Data Licensing

Newly written code in this repository is licensed under MIT. Third-party data licensing, access notes, and usage caveats are documented separately in [docs/data_provenance.md](docs/data_provenance.md).

## Future Improvements

- add stable database integration tests to CI once the container workflow is fully validated
- add a live PostGIS export of the same reconciliation logic for container-only workflows
- extend historical-site and facility analyses to additional park-unit categories when source coverage is sufficient
