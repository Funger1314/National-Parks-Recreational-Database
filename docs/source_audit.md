# Source Audit

## Files Inspected

- PostgreSQL custom-format dump: `NP_Database_postgres_Group1.sql`
- Original report: `Geog 574_Final Report_Group 1.pdf`

## Actual Database Format

- `file` identifies the dump as `PostgreSQL custom database dump - v1.13-0`.
- The dump header records database and server version `10.22`.
- The dump name is `Final_Project`.
- The backup includes PostgreSQL extension entries, table DDL, table data, sequences, primary keys, and GiST indexes.

## Report Findings Recovered Before Rebuilding

From the report:

- Pages 1-2 define the problem statement, research questions, and data sources.
- Pages 6-8 describe the non-spatial visitation workflow, including generic `Field1`, `Field2`, and merged CSV logic.
- Pages 8-11 describe spatial preprocessing, projection standardization, and the original PostgreSQL import workflow.
- Pages 12-15 preserve the five original SQL questions and their narrative interpretation.
- Figure 2-1 is the conceptual ERD.
- Figure 2-2 is the relational schema diagram.
- Figure 3-2, Figure 3-3, and Figure 3-4 preserve small Python code screenshots from the original notebook workflow.
- Figure 4-1 preserves the original Rocky Mountain amenity map.

## Database Object Inventory

### Schemas and Extensions

Schemas referenced in the dump:

- `public`
- `tiger`
- `tiger_data`
- `topology`

Extensions referenced in the dump:

- `plpgsql`
- `address_standardizer`
- `fuzzystrmatch`
- `ogr_fdw`
- `postgis`
- `pgrouting`
- `pointcloud`
- `pointcloud_postgis`
- `postgis_raster`
- `postgis_sfcgal`
- `postgis_tiger_geocoder`
- `postgis_topology`

### Core Tables and Row Counts

| Table | Actual rows | Geometry type | Notes |
| --- | ---: | --- | --- |
| `np_visitation` | 2,064 | none | 4 parks x 43 years x 12 months |
| `nps_boundary` | 72 | `MultiPolygon` | 4 invalid geometries |
| `nps_facilities` | 21,904 | `Point` | nationwide layer |
| `nrhp_points` | 67,443 | `Point` | nationwide layer |
| `park_roads` | 4,315 | `MultiLineStringZ/M` | 4 parks only |
| `park_trails` | 1,152 | `MultiLineString` | 4 parks only |
| `parking_areas` | 872 | `PointZ/M` | 4 parks only |

### Keys and Indexes

Recovered primary keys:

- `np_visitation(id)`
- `nps_boundary(parkname)`
- `nps_facilities(gid)`
- `nrhp_points(gid)`
- `park_roads(gid)`
- `park_trails(gid)`
- `parking_areas(gid)`

Recovered spatial indexes:

- `nps_boundary_geom_idx`
- `nps_facilities_geom_idx`
- `nrhp_points_geom_idx`
- `park_roads_geom_idx`
- `park_trails_geom_idx`
- `parking_areas_geom_idx`

Recovered foreign keys:

- none in the actual backup

## Recovered Code and Queries

### Python Workflow Fragments Recovered from the Report

- A loop over `['Rocky Mountain', 'Great Smoky Mountains', 'Grand Teton', 'Assateague Island']`
- A matching abbreviation list `['ROMO', 'GRSM', 'GRTE', 'ASIS']`
- `pd.read_csv(file_name, skiprows=3, usecols=range(14))`
- a rename block starting from `Field1` and `Field2`
- `pd.concat(map(pd.read_csv, [...] ), ignore_index=True)`
- a `DataFrame.max()` screenshot used to inspect field lengths

These screenshots support the reconstructed ETL package, but they do not reveal the full original notebook or all intermediate files.

### SQL Queries Recovered from the Report

The five original SQL questions are preserved in `sql/legacy/02_original_report_queries.sql`. They were transcribed from report pages 12-15 and intentionally retain historical issues such as:

- `SERIAL` misuse in the visitation table design discussion
- count inflation risk in Question 3
- `ST_Contains` dependence for road counting
- rounded acres conversion in Question 1

## Geometry and CRS Observations

- All geometry columns in the recovered DDL declare SRID `102003`.
- Geometry type declarations match the legacy tables:
  - `nps_boundary`: `MultiPolygon`
  - `nps_facilities`: `Point`
  - `nrhp_points`: `Point`
  - `park_roads`: `MultiLineStringZM`
  - `park_trails`: `MultiLineString`
  - `parking_areas`: `PointZM`
- `ESRI:102003` is not equivalent to `EPSG:5070`.
  - `ESRI:102003` uses latitude of false origin `37.5`
  - `EPSG:5070` uses latitude of false origin `23`

## Legacy Technical Issues

- The visitation table encodes ordinary measures as sequence-backed integers because the original implementation modeled those columns as `SERIAL`.
- `nps_boundary` contains 4 invalid polygons.
- The boundary table has 72 rows, but the recovered sequence was last set to 428, which indicates deleted or removed features during the original cleanup process.
- `park_roads`, `park_trails`, and `parking_areas` only cover four focal parks.
- `nps_facilities` and `nrhp_points` are nationwide tables and are not limited to the focal parks.
- The dump references optional extensions that are not required by the project tables and may not exist in a default `postgis/postgis` container.

## Differences Between the Report Design and the Actual Backup

1. The report's relational diagram shows `boundary_gid` foreign-key style relationships, but the actual backup contains no foreign-key constraints.
2. The report discussion emphasizes `gid` and geometry links, but the actual boundary primary key is `parkname`.
3. The report describes cleaning the boundary dataset from 428 to 72 parks; the backup confirms 72 final records but also preserves the historical `gid` sequence at 428.
4. The report describes the visitation table as a manually created import target; the backup confirms the legacy table shape but also exposes sequence-backed numeric columns.
5. The report implies broad park coverage conceptually, while the operational spatial coverage is narrow for roads, trails, and parking.

## Missing Original Assets

Unavailable from the supplied materials:

- the original raw visitation CSV files
- the original shapefiles
- the original ArcGIS Pro project
- the original Excel workbook used for facility-code decoding
- the original Jupyter notebook
- the original pgAdmin restore history or import session logs

## What Can Be Reproduced

- legacy table exports from the recovered dump
- the final merged visitation table
- the five report-era analytical questions
- selected spatial analyses and figures using recovered data
- a modernized schema and migration workflow

## What Cannot Be Reproduced Exactly

- every original ArcGIS edit session
- every original raw-to-final visitation transformation without the raw CSV files
- the exact original notebook source
- the exact original shapefile inventory and field history
- the exact 2022 execution environment

