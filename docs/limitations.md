# Limitations

- Only four parks have detailed visitation, road, trail, and parking coverage in the recovered project scope.
- Spatial datasets are incomplete and uneven across park units.
- The original raw visitation CSV files were not supplied with this reconstruction task.
- The original shapefiles were not supplied with this reconstruction task.
- The original ArcGIS Pro project was not supplied.
- The original Jupyter notebook was not supplied.
- Python code had to be reconstructed from report screenshots and narrative description.
- Some original preprocessing depended on Excel and ArcGIS Pro.
- The legacy visitation design incorrectly modeled ordinary measures as sequence-backed numeric columns.
- The conceptual foreign-key relationships shown in the report are not enforced in the actual backup.
- Park names differ across tables and require explicit alias handling.
- Line features represent segmented geometries, not unique road or trail networks.
- Facility points should not be interpreted as a complete current amenity inventory.
- `ST_Contains` can omit boundary-crossing lines and points that only touch the border.
- Visitation-per-area is only a proxy for pressure, not a direct overcrowding measurement.
- The recovered data reflects the source period around 2022 and should not be represented as current operational data.
- The reconstructed scripts, SQL, and tests may differ from the original implementation.
- The current local environment did not provide native `pg_restore`, `psql`, or Docker during reconstruction execution, so some live database steps are scaffolded rather than run here.

