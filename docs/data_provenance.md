# Data Provenance

The repository records provenance in [data/source_manifest.yml](../data/source_manifest.yml). The entries were reconstructed from report pages 1-2 and page 16.

## Source Summary

- NPS visitation data: `https://irma.nps.gov/STATS/`
- NPS boundaries, roads, trails, and parking: `https://public-nps.opendata.arcgis.com/`
- NPS National Register of Historic Places data: `https://www.nps.gov/subjects/nationalregister/database-research.htm`
- USDA Forest Service recreation facilities: `https://data.fs.usda.gov/geodata/edw/datasets.php?xmlKeyword=camp`

## Access Dates Recovered from the Report

- November 2022 for most NPS downloads
- November and December 2022 for visitation data
- December 2022 for the USDA recreation-facility layer

## Availability Status

- The original raw files were not supplied with the current reconstruction task.
- The legacy PostgreSQL/PostGIS dump preserves processed tables recovered from those sources.
- The visitation workflow can be reconstructed from raw CSV exports when they are made available.

## Checksums

No checksums are fabricated for unavailable source files.

