"""Project-wide configuration constants and path helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

VISITATION_FINAL_COLUMNS = [
    "year",
    "month",
    "recreation_visitors",
    "non_recreation_visitors",
    "recreation_hr",
    "non_recreation_hr",
    "concession_lodging",
    "tent_campers",
    "rv_campers",
    "concession_camping",
    "backcountry_campers",
    "misc_campers",
    "non_recreation_overnight_stays",
    "total_overnight_stays",
    "np_name",
]

VISITATION_NUMERIC_COLUMNS = [
    "year",
    "recreation_visitors",
    "non_recreation_visitors",
    "recreation_hr",
    "non_recreation_hr",
    "concession_lodging",
    "tent_campers",
    "rv_campers",
    "concession_camping",
    "backcountry_campers",
    "misc_campers",
    "total_overnight_stays",
]

VISITATION_COLUMN_SYNONYMS = {
    "Field1": "year",
    "Field2": "month",
    "Field3": "recreation_visitors",
    "Field4": "non_recreation_visitors",
    "Field5": "recreation_hr",
    "Field6": "non_recreation_hr",
    "Field7": "concession_lodging",
    "Field8": "tent_campers",
    "Field9": "rv_campers",
    "Field10": "concession_camping",
    "Field11": "backcountry_campers",
    "Field12": "misc_campers",
    "Field13": "non_recreation_overnight_stays",
    "Field14": "total_overnight_stays",
    "Year": "year",
    "Month": "month",
    "Recreation Visitors": "recreation_visitors",
    "Non-Recreation Visitors": "non_recreation_visitors",
    "RecreationHours": "recreation_hr",
    "NonRecreationHours": "non_recreation_hr",
    "Concession Lodging": "concession_lodging",
    "Tent Campers": "tent_campers",
    "RV Campers": "rv_campers",
    "Concession Camping": "concession_camping",
    "Backcountry Campers": "backcountry_campers",
    "Misc Campers": "misc_campers",
    "NonRecreationOvernightStays": "non_recreation_overnight_stays",
    "TotalOvernightStays": "total_overnight_stays",
}

MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

PARK_ABBREVIATIONS = {
    "ROMO": "Rocky Mountain",
    "GRSM": "Great Smoky Mountain",
    "GRTE": "Grand Teton",
    "ASIS": "Assateague Island",
}

PARK_ALIAS_MAP = {
    "Rocky Mountain": "Rocky Mountain",
    "Rocky Mountain National Park": "Rocky Mountain",
    "Great Smoky Mountain": "Great Smoky Mountain",
    "Great Smoky Mountains": "Great Smoky Mountain",
    "Great Smoky Mountains National Park": "Great Smoky Mountain",
    "Grand Teton": "Grand Teton",
    "Grand Teton National Park": "Grand Teton",
    "Assateague Island": "Assateague Island",
    "Assateague Island National Seashore": "Assateague Island",
}

SPATIAL_TABLE_GEOMETRY_COLUMNS = {
    "nps_boundary": "geom",
    "nps_facilities": "geom",
    "nrhp_points": "geom",
    "park_roads": "geom",
    "park_trails": "geom",
    "parking_areas": "geom",
}


@dataclass(slots=True)
class ProjectPaths:
    """Common repository paths."""

    root: Path

    @property
    def raw_visitation_dir(self) -> Path:
        return self.root / "data" / "raw" / "visitation"

    @property
    def recovered_dir(self) -> Path:
        return self.root / "data" / "recovered"

    @property
    def processed_dir(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def query_results_dir(self) -> Path:
        return self.root / "outputs" / "query_results"

    @property
    def quality_reports_dir(self) -> Path:
        return self.root / "outputs" / "quality_reports"

    @property
    def figures_dir(self) -> Path:
        return self.root / "outputs" / "figures"


def project_paths() -> ProjectPaths:
    return ProjectPaths(root=Path(__file__).resolve().parents[2])

