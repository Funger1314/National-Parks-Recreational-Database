# Legacy vs Modern

| Topic | Legacy recovery | Modernized implementation |
| --- | --- | --- |
| Storage target | `public.*` restored tables | `core.*`, `analytics.*`, `metadata.*` schemas |
| Naming | original table and field names | consistent snake_case plus canonical park names |
| Constraints | primary keys only, no foreign keys | identity keys, foreign keys, uniqueness, checks |
| Provenance | implicit in recovered dump | explicit source-dataset metadata and alias tables |
| Visitation ETL | original notebook unavailable | package-based deterministic workflow |
| Migration acceptance | no table-by-table reconciliation artifact | `outputs/quality_reports/migration_reconciliation.csv` enforces row-balance checks and documents unresolved associations |
| Query logic | report-era SQL preserved verbatim | corrected SQL with documented fixes |
| Quality checks | ad hoc in report narrative | explicit spatial and data-quality checks |
| Reproducibility | pgAdmin and ArcGIS-dependent originally | Python package, SQL files, scripts, and Docker workflow |
