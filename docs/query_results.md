# Query Results

All results below were recomputed from the recovered dump on 2026-07-15.

## Q1. Colorado Parks and Area

Schema used: recovered legacy data

Units:

- area in acres
- area in square kilometers

Results:

| Park | Acres | Square kilometers |
| --- | ---: | ---: |
| Black Canyon of the Gunnison | 31,227.96 | 126.39 |
| Great Sand Dunes | 107,580.50 | 435.40 |
| Mesa Verde | 53,688.36 | 217.28 |
| Rocky Mountain | 267,061.31 | 1,080.61 |

## Q2. Total Visitation, 2010-2020

Schema used: recovered legacy data

Units: visits

| Park | Visitors 2010-2020 |
| --- | ---: |
| Assateague Island | 24,487,156 |
| Grand Teton | 49,275,453 |
| Great Smoky Mountain | 237,633,203 |
| Rocky Mountain | 41,884,781 |

Interpretation:

Great Smoky Mountain dominates the four-park visitation subset during 2010-2020.

## Q3. Rocky Mountain Amenity Counts

Schema used: recovered legacy data

Units: feature records

| Metric | Value |
| --- | ---: |
| campground records | 7 |
| historic-site records | 25 |
| trail records | 490 |
| distinct trail names | 159 |
| unnamed trail records | 0 |
| parking-area records | 133 |

Interpretation:

The corrected query avoids multiplying campground and historical-site counts through a many-to-many join.

## Q4. Unpaved Roads

Schema used: recovered legacy data

Units:

- counts are feature records
- lengths are kilometers

| Park | `ST_Contains` count | `ST_Contains` km | `ST_Intersects` count | intersected geom km | clipped km |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rocky Mountain | 24 | 26.49 | 28 | 54.58 | 47.79 |
| Great Smoky Mountain | 105 | 92.99 | 109 | 107.76 | 107.44 |
| Grand Teton | 490 | 162.77 | 497 | 174.23 | 173.86 |

Interpretation:

Containment-based counts understate road coverage relative to intersection-based and clipped-length approaches.

## Q5. Parks Above the Four-Park Average Total Visitation

Schema used: recovered legacy data

Units: visits

- Four-park average total visitation: 303,032,272
- Park above that threshold: Great Smoky Mountain

Coverage limitation:

The comparison is limited to the four parks represented in the visitation table.

