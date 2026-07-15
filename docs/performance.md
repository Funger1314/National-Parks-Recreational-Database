# Performance Notes

This repository includes prepared performance-check SQL in `sql/analytics/05_performance_checks.sql`.

## Current Status

- The legacy dump itself preserves GiST indexes on all spatial tables.
- The modern core schema adds GiST and B-tree indexes aligned with common analytical filters.
- Actual `EXPLAIN ANALYZE` timings were not collected in the current local reconstruction environment because a live Docker/PostGIS runtime was not exercised here.

## Intended Checks

- verify GiST index usage for point-in-polygon joins
- compare containment versus intersection predicates
- avoid repeated `ST_Intersection` work where a cheaper predicate can prefilter candidates
- document timing only after it has been measured

