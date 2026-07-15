# Data Dictionary

## Legacy Tables

### `legacy.np_visitation`

- `id`: recovered row identifier
- `year`: visitation year
- `month`: month name
- `recreation_visitors`, `non_recreation_visitors`: monthly visitor counts
- `recreation_hr`, `non_recreation_hr`: hour-based visitation measures
- `concession_lodging`, `tent_campers`, `rv_campers`, `concession_camping`, `backcountry_campers`, `misc_campers`: overnight or activity-specific measures
- `non_recreation_overnight_stays`, `total_overnight_stays`: overnight stay fields
- `np_name`: legacy park name label

### `legacy.nps_boundary`

- `gid`: recovered source identifier
- `state`: two-letter state code
- `unit_type`: park unit category
- `metadata`: descriptive source note
- `parkname`: park name
- `shape_area`, `shape_length`: stored geometry metrics from the original import
- `geom`: `MultiPolygon`, SRID `102003`

### `legacy.nps_facilities`

- `gid`: recovered source identifier
- `notes`: free-text note
- `facility_type`: decoded facility category
- `geom`: `Point`, SRID `102003`

### `legacy.nrhp_points`

- `gid`: recovered source identifier
- `nris_refnu`: NRHP reference number
- `resname`, `restype`: resource descriptors
- `address`, `city`, `county`, `state`, `status`, `listed_date`: descriptive attributes
- `geom`: `Point`, SRID `102003`

### `legacy.park_roads`

- `gid`: recovered source identifier
- `park_name`: park label
- `road_name`: road name
- `shape_length`: stored line length from original import
- `rdsurface`: surface class
- `seasonal`, `seasdesc`: seasonal access attributes
- `geom`: `MultiLineStringZM`, SRID `102003`

### `legacy.park_trails`

- `gid`: recovered source identifier
- `park_name`: park label
- `trailname`, `trailtype`, `trluse`, `hist_signf`: trail descriptors
- `shape_leng`: stored line length from original import
- `geom`: `MultiLineString`, SRID `102003`

### `legacy.parking_areas`

- `gid`: recovered source identifier
- `park_name`: park label
- `lottype`, `rte_name`, `surface`: parking descriptors
- `total_space`, `handicapped`: count fields
- `seasonal`, `yearblt`, `notes`: supporting attributes
- `geom`: `PointZM`, SRID `102003`

## Core Tables

- `core.park`: canonical park reference geometry and metadata
- `core.visitation`: normalized monthly visitation keyed to `park_id`
- `core.facility`: point features such as campgrounds
- `core.historic_site`: normalized NRHP points
- `core.road`: road segments with normalized park mapping
- `core.trail`: trail segments with normalized park mapping
- `core.parking_area`: parking features with normalized park mapping

