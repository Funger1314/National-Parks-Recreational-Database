# Database Design

## Legacy Layer

Recovered legacy tables:

- `legacy.np_visitation`
- `legacy.nps_boundary`
- `legacy.nps_facilities`
- `legacy.nrhp_points`
- `legacy.park_roads`
- `legacy.park_trails`
- `legacy.parking_areas`

These compatibility views expose the restored `public.*` tables under a stable schema name for modern SQL.

## Modern Core Tables

- `core.park`
- `core.visitation`
- `core.facility`
- `core.historic_site`
- `core.road`
- `core.trail`
- `core.parking_area`

## Design Decisions

- surrogate keys use generated identity columns
- source identifiers such as `gid` and `id` are preserved
- park names are normalized through `metadata.park_name_alias`
- geometry columns retain SRID `102003`
- `park_id` is nullable for records that cannot be resolved confidently
- migration never overwrites the legacy restore

## Park Resolution Strategy

- `np_visitation`, `park_roads`, `park_trails`, and `parking_areas` use explicit name aliasing
- `nps_facilities` and `nrhp_points` use spatial containment against park boundaries
- unresolved records remain nullable rather than being forced into ambiguous park assignments

