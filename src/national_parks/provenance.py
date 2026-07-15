"""Source manifest helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

SOURCE_MANIFEST = {
    "datasets": [
        {
            "dataset_name": "National Park Service visitation data",
            "source_agency": "National Park Service",
            "original_url": "https://irma.nps.gov/STATS/",
            "access_date_from_report": "November and December 2022",
            "file_format": "CSV",
            "original_crs": None,
            "stored_crs": None,
            "expected_record_count": 2064,
            "derived_tables": ["np_visitation", "core.visitation"],
            "processing_steps": [
                "Rename generic CSV fields.",
                "Append canonical park name column.",
                "Convert numeric strings to numeric values.",
                "Merge four park files into a single table.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use NPS terms for public datasets.",
            "known_limitations": (
                "Only four parks are represented in the recovered visitation table."
            ),
        },
        {
            "dataset_name": "NPS park boundaries",
            "source_agency": "National Park Service",
            "original_url": "https://public-nps.opendata.arcgis.com/",
            "access_date_from_report": "November 2022",
            "file_format": "Shapefile",
            "original_crs": "varied prior to reprojection",
            "stored_crs": "ESRI:102003",
            "expected_record_count": 72,
            "derived_tables": ["nps_boundary", "core.park"],
            "processing_steps": [
                "Retain relevant columns.",
                "Remove duplicate and non-target park-unit records.",
                "Reproject to a shared Albers equal-area CRS.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use NPS terms for public datasets.",
            "known_limitations": "Four geometries are invalid in the recovered legacy backup.",
        },
        {
            "dataset_name": "NPS roads",
            "source_agency": "National Park Service",
            "original_url": "https://public-nps.opendata.arcgis.com/",
            "access_date_from_report": "November 2022",
            "file_format": "Shapefile",
            "original_crs": "varied prior to reprojection",
            "stored_crs": "ESRI:102003",
            "expected_record_count": 4315,
            "derived_tables": ["park_roads", "core.road"],
            "processing_steps": [
                "Normalize park-specific field structures.",
                "Add or join park-name fields when missing.",
                "Merge park-specific road layers.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use NPS terms for public datasets.",
            "known_limitations": "Only four parks have roads in the recovered project scope.",
        },
        {
            "dataset_name": "NPS trails",
            "source_agency": "National Park Service",
            "original_url": "https://public-nps.opendata.arcgis.com/",
            "access_date_from_report": "November 2022",
            "file_format": "Shapefile",
            "original_crs": "varied prior to reprojection",
            "stored_crs": "ESRI:102003",
            "expected_record_count": 1152,
            "derived_tables": ["park_trails", "core.trail"],
            "processing_steps": [
                "Normalize park-specific field structures.",
                "Merge park-specific trail layers.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use NPS terms for public datasets.",
            "known_limitations": (
                "Line records represent segmented features rather than unique trail networks."
            ),
        },
        {
            "dataset_name": "NPS parking areas",
            "source_agency": "National Park Service",
            "original_url": "https://public-nps.opendata.arcgis.com/",
            "access_date_from_report": "November 2022",
            "file_format": "Shapefile",
            "original_crs": "varied prior to reprojection",
            "stored_crs": "ESRI:102003",
            "expected_record_count": 872,
            "derived_tables": ["parking_areas", "core.parking_area"],
            "processing_steps": [
                "Normalize park-specific field structures.",
                "Merge park-specific parking layers.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use NPS terms for public datasets.",
            "known_limitations": (
                "Only four parks have parking-area coverage in the recovered backup."
            ),
        },
        {
            "dataset_name": "National Register of Historic Places points",
            "source_agency": "National Park Service",
            "original_url": "https://www.nps.gov/subjects/nationalregister/database-research.htm",
            "access_date_from_report": "November 2022",
            "file_format": "Shapefile",
            "original_crs": "unknown from report",
            "stored_crs": "ESRI:102003",
            "expected_record_count": 67443,
            "derived_tables": ["nrhp_points", "core.historic_site"],
            "processing_steps": [
                "Retain relevant descriptive and locational columns.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use NPS terms for public datasets.",
            "known_limitations": (
                "Nationwide coverage extends beyond the four focal parks in the project analysis."
            ),
        },
        {
            "dataset_name": "USDA Forest Service recreational facilities",
            "source_agency": "United States Department of Agriculture Forest Service",
            "original_url": "https://data.fs.usda.gov/geodata/edw/datasets.php?xmlKeyword=camp",
            "access_date_from_report": "December 2022",
            "file_format": "Shapefile",
            "original_crs": "unknown from report",
            "stored_crs": "ESRI:102003",
            "expected_record_count": 21904,
            "derived_tables": ["nps_facilities", "core.facility"],
            "processing_steps": [
                "Decode numeric facility codes in Excel.",
                "Join cleaned codes back to the spatial layer.",
                "Delete irrelevant fields before import.",
            ],
            "original_file_available": False,
            "recovered_from_database": True,
            "licensing_notes": "Use USDA-FS terms for public datasets.",
            "known_limitations": (
                "The layer contains national coverage beyond the focal parks and may not "
                "represent a complete current amenity inventory."
            ),
        },
    ]
}


def write_source_manifest(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(SOURCE_MANIFEST, handle, sort_keys=False, allow_unicode=False)
    return output_path
