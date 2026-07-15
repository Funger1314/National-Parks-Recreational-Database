# Methodology

## Reconstruction Approach

The reconstruction followed two complementary workflows:

- Workflow A reconstructs the raw visitation merge process from NPS CSV files placed in `data/raw/visitation/`.
- Workflow B recovers the final `np_visitation` table directly from the legacy PostgreSQL/PostGIS dump and exports it to CSV.

Workflow B recovers an already-processed table and therefore does not recreate every original raw transformation step.

## Report-Guided ETL Reconstruction

The Python ETL package was reconstructed from report pages 6-8 and the embedded code screenshots. The resulting implementation:

- validates file existence with `pathlib`
- handles generic fields such as `Field1`, `Field2`, and related aliases
- strips commas from numeric strings before coercion
- standardizes month names
- standardizes park names using an explicit alias map
- checks year ranges and nonnegative count fields
- reports duplicate `(park, year, month)` combinations
- writes deterministic CSV output and quality reports

## Legacy Dump Analysis

Because the current local environment did not provide `pg_restore` or `psql`, the supplied custom dump was also analyzed directly with `pgdumplib` and Python. This enabled:

- table inventory
- recovered row counts
- CSV export of `np_visitation`
- geometry parsing with Shapely
- recovered query reproduction without fabricating results

The repository still includes Docker/PostGIS restore scripts for a full database workflow.

## Migration Reconciliation

The modernization acceptance workflow now generates
`outputs/quality_reports/migration_reconciliation.csv`.

For each migrated table, the report records:

- legacy row count
- migrated row count
- excluded row count
- duplicate row count
- unresolved park-association count
- null-geometry count
- invalid-geometry count
- repaired-geometry count
- transformed-column count
- a plain-English discrepancy explanation

The report enforces the invariant:

`legacy rows = migrated rows + excluded rows + duplicate removals`

If the equation fails for any table, report generation and migration tests fail.

## Spatial Data Checks

Geometry quality checks were performed against the recovered WKB geometry values and summarized in `outputs/quality_reports/spatial_quality_summary.csv`.

Observed results:

- `nps_boundary`: 72 rows, 4 invalid polygons
- `nps_facilities`: 21,904 valid points
- `nrhp_points`: 67,443 valid points
- `park_roads`: 4,315 valid multi-line geometries with Z/M values
- `park_trails`: 1,152 valid multi-line geometries
- `parking_areas`: 872 valid points with Z/M values

## CRS Verification

The recovered geometry columns are declared with SRID `102003`.

Comparison with `EPSG:5070` shows they are not interchangeable:

- `ESRI:102003`: latitude of false origin `37.5`
- `EPSG:5070`: latitude of false origin `23`

Both are Albers equal-area systems over NAD83, but they are not the same CRS definition.

## Analytical Reproduction

The five original questions were recomputed from the recovered dump, not inferred from the report narrative alone. The modernized query set additionally documents:

- unit conversions
- containment versus intersection differences
- count inflation pitfalls in many-to-many joins
- record-count versus unique-feature-count distinctions

## Quality Caveats

- `nps_boundary` invalid geometries are preserved in legacy form and repaired in `core.park`.
- The nationwide `nrhp_points` and `nps_facilities` layers are broader than the four focal parks used in the original project questions.
- Roads, trails, and parking layers are incomplete outside the four focal parks.
- Some territory-scale NRHP points fall outside the intended contiguous-U.S. analysis footprint of the chosen CRS.
