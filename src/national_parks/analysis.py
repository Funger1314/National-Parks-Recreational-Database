"""Recovered-data analysis and figure generation."""

from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parents[2] / "work" / "mplconfig"),
)

import matplotlib.pyplot as plt
import pandas as pd
from pyproj import CRS
from shapely import from_wkb

from national_parks.config import MONTH_ORDER, project_paths
from national_parks.database import load_legacy_dump, table_to_dataframe
from national_parks.migration import write_migration_reconciliation


def _geometry_from_hex(value: str):
    return from_wkb(bytes.fromhex(value))


def load_public_tables(dump_path: Path) -> dict[str, pd.DataFrame]:
    dump = load_legacy_dump(dump_path)
    tables = {}
    for table in [
        "np_visitation",
        "nps_boundary",
        "nps_facilities",
        "nrhp_points",
        "park_roads",
        "park_trails",
        "parking_areas",
    ]:
        tables[table] = table_to_dataframe(dump, "public", table)
    return tables


def compare_reference_systems() -> dict[str, object]:
    esri_102003 = CRS.from_authority("ESRI", "102003")
    epsg_5070 = CRS.from_epsg(5070)
    return {
        "stored_srid": 102003,
        "stored_name": esri_102003.name,
        "stored_proj4": esri_102003.to_proj4(),
        "comparison_srid": 5070,
        "comparison_name": epsg_5070.name,
        "comparison_proj4": epsg_5070.to_proj4(),
        "semantically_equal": esri_102003.equals(epsg_5070),
        "exact_same": esri_102003.is_exact_same(epsg_5070),
    }


def spatial_quality_summary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    specs = {
        "nps_boundary": "geom",
        "nps_facilities": "geom",
        "nrhp_points": "geom",
        "park_roads": "geom",
        "park_trails": "geom",
        "parking_areas": "geom",
    }
    rows: list[dict[str, object]] = []
    for table_name, geom_column in specs.items():
        frame = tables[table_name]
        null_count = 0
        empty_count = 0
        invalid_count = 0
        has_z_count = 0
        geometry_types: Counter[str] = Counter()
        bounds = [None, None, None, None]
        for geom_hex in frame[geom_column]:
            if geom_hex in (None, "", "\\N"):
                null_count += 1
                continue
            geom = _geometry_from_hex(geom_hex)
            geometry_types[geom.geom_type] += 1
            empty_count += int(geom.is_empty)
            invalid_count += int(not geom.is_valid)
            has_z_count += int(geom.has_z)
            minx, miny, maxx, maxy = geom.bounds
            if bounds[0] is None:
                bounds = [minx, miny, maxx, maxy]
            else:
                bounds = [
                    min(bounds[0], minx),
                    min(bounds[1], miny),
                    max(bounds[2], maxx),
                    max(bounds[3], maxy),
                ]
        rows.append(
            {
                "table_name": table_name,
                "row_count": len(frame),
                "null_geometry_count": null_count,
                "empty_geometry_count": empty_count,
                "invalid_geometry_count": invalid_count,
                "geometry_types": "; ".join(
                    f"{name}:{count}" for name, count in sorted(geometry_types.items())
                ),
                "has_z_count": has_z_count,
                "min_x": bounds[0],
                "min_y": bounds[1],
                "max_x": bounds[2],
                "max_y": bounds[3],
            }
        )
    return pd.DataFrame(rows)


def original_query_results(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    visitation = tables["np_visitation"].copy()
    visitation["year"] = visitation["year"].astype(int)
    visitation["total_visitors"] = (
        visitation["recreation_visitors"].astype(int)
        + visitation["non_recreation_visitors"].astype(int)
    )

    boundaries = tables["nps_boundary"].copy()
    facilities = tables["nps_facilities"].copy()
    nrhp = tables["nrhp_points"].copy()
    roads = tables["park_roads"].copy()
    trails = tables["park_trails"].copy()
    parking = tables["parking_areas"].copy()

    q1_rows = []
    for row in boundaries.itertuples(index=False):
        if row.state == "CO":
            geom = _geometry_from_hex(row.geom)
            q1_rows.append(
                {
                    "state": row.state,
                    "park_name": row.parkname,
                    "area_acres": geom.area / 4046.8564224,
                    "area_sq_km": geom.area / 1_000_000,
                }
            )
    q1 = pd.DataFrame(q1_rows).sort_values("park_name").reset_index(drop=True)

    q2 = (
        visitation.loc[visitation["year"].between(2010, 2020)]
        .groupby("np_name", as_index=False)["total_visitors"]
        .sum()
        .rename(columns={"total_visitors": "visitors_2010_2020"})
        .sort_values("np_name")
        .reset_index(drop=True)
    )

    rocky_boundary_hex = boundaries.loc[boundaries["parkname"] == "Rocky Mountain", "geom"].iloc[0]
    rocky_boundary = _geometry_from_hex(rocky_boundary_hex)
    campground_records = sum(
        1
        for row in facilities.itertuples(index=False)
        if row.facility_type == "Campground"
        and rocky_boundary.contains(_geometry_from_hex(row.geom))
    )
    nrhp_records = sum(
        1
        for row in nrhp.itertuples(index=False)
        if rocky_boundary.contains(_geometry_from_hex(row.geom))
    )
    rocky_trails = trails.loc[trails["park_name"] == "Rocky Mountain"]
    q3 = pd.DataFrame(
        [
            {
                "park_name": "Rocky Mountain",
                "campground_records": campground_records,
                "nrhp_records": nrhp_records,
                "trail_records": len(rocky_trails),
                "distinct_trail_names": (
                    rocky_trails["trailname"].replace("", pd.NA).dropna().nunique()
                ),
                "unnamed_trail_records": rocky_trails["trailname"].replace("", pd.NA).isna().sum(),
                "parking_records": int((parking["park_name"] == "Rocky Mountain").sum()),
            }
        ]
    )

    q4_rows = []
    unpaved_mask = roads["rdsurface"].isin(["Native or Dirt", "Gravel"])
    for park_name in ["Rocky Mountain", "Great Smoky Mountain", "Grand Teton"]:
        boundary = _geometry_from_hex(
            boundaries.loc[boundaries["parkname"] == park_name, "geom"].iloc[0]
        )
        contains_count = 0
        contains_length = 0.0
        intersects_count = 0
        intersects_length = 0.0
        clipped_length = 0.0
        for row in roads.loc[unpaved_mask].itertuples(index=False):
            geom = _geometry_from_hex(row.geom)
            if boundary.contains(geom):
                contains_count += 1
                contains_length += float(row.shape_length)
            if boundary.intersects(geom):
                intersects_count += 1
                intersects_length += geom.length
                clipped_length += boundary.intersection(geom).length
        q4_rows.append(
            {
                "park_name": park_name,
                "contains_count": contains_count,
                "contains_length_km": contains_length / 1000,
                "intersects_count": intersects_count,
                "intersects_length_km": intersects_length / 1000,
                "clipped_length_km": clipped_length / 1000,
            }
        )
    q4 = pd.DataFrame(q4_rows)

    q5_totals = (
        visitation.groupby("np_name", as_index=False)["total_visitors"]
        .sum()
        .rename(columns={"total_visitors": "total_visitation"})
    )
    average_total = q5_totals["total_visitation"].mean()
    q5 = q5_totals.assign(
        average_total_visitation=average_total,
        is_above_average=lambda frame: frame["total_visitation"] > average_total,
    ).sort_values("np_name")

    return {
        "q1_colorado_parks_area": q1,
        "q2_visitation_2010_2020": q2,
        "q3_rocky_mountain_amenity_counts": q3,
        "q4_unpaved_road_lengths": q4,
        "q5_parks_above_average_total_visitation": q5,
    }


def advanced_analysis_results(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    visitation = tables["np_visitation"].copy()
    boundaries = tables["nps_boundary"].copy()
    roads = tables["park_roads"].copy()
    trails = tables["park_trails"].copy()
    parking = tables["parking_areas"].copy()
    nrhp = tables["nrhp_points"].copy()

    visitation["year"] = visitation["year"].astype(int)
    visitation["total_visitors"] = (
        visitation["recreation_visitors"].astype(int)
        + visitation["non_recreation_visitors"].astype(int)
    )
    visitation["month"] = pd.Categorical(visitation["month"], categories=MONTH_ORDER, ordered=True)

    seasonality = (
        visitation.groupby(["np_name", "month"], as_index=False)["total_visitors"]
        .mean()
        .rename(columns={"total_visitors": "avg_monthly_visitors"})
        .sort_values(["np_name", "month"])
        .reset_index(drop=True)
    )

    area_rows = []
    for row in boundaries.itertuples(index=False):
        area_sq_km = _geometry_from_hex(row.geom).area / 1_000_000
        area_rows.append({"park_name": row.parkname, "area_sq_km": area_sq_km})
    areas = pd.DataFrame(area_rows)

    annual_visits = (
        visitation.groupby(["np_name", "year"], as_index=False)["total_visitors"]
        .sum()
        .rename(columns={"np_name": "park_name"})
    )
    annual_visits = annual_visits.loc[annual_visits["year"].between(2010, 2020)]
    visitation_pressure = (
        annual_visits.groupby("park_name", as_index=False)["total_visitors"]
        .mean()
        .merge(areas, on="park_name", how="left")
    )
    visitation_pressure["avg_annual_visitors_per_sq_km"] = (
        visitation_pressure["total_visitors"] / visitation_pressure["area_sq_km"]
    )

    infrastructure_rows = []
    for park_name in ["Rocky Mountain", "Great Smoky Mountain", "Grand Teton", "Assateague Island"]:
        area_sq_km = float(areas.loc[areas["park_name"] == park_name, "area_sq_km"].iloc[0])
        road_km = (
            roads.loc[roads["park_name"] == park_name, "shape_length"].astype(float).sum() / 1000
        )
        trail_km = (
            trails.loc[trails["park_name"] == park_name, "shape_leng"].astype(float).sum() / 1000
        )
        parking_count = int((parking["park_name"] == park_name).sum())
        infrastructure_rows.append(
            {
                "park_name": park_name,
                "road_km_per_100_sq_km": road_km / area_sq_km * 100,
                "trail_km_per_100_sq_km": trail_km / area_sq_km * 100,
                "parking_records_per_100_sq_km": parking_count / area_sq_km * 100,
            }
        )
    infrastructure_density = pd.DataFrame(infrastructure_rows)

    boundary_geoms = {
        row.parkname: _geometry_from_hex(row.geom) for row in boundaries.itertuples(index=False)
    }
    completeness_rows = []
    for park_name in ["Rocky Mountain", "Great Smoky Mountain", "Grand Teton", "Assateague Island"]:
        boundary = boundary_geoms[park_name]
        completeness_rows.append(
            {
                "park_name": park_name,
                "visitation": park_name in set(visitation["np_name"]),
                "roads": park_name in set(roads["park_name"]),
                "trails": park_name in set(trails["park_name"]),
                "parking": park_name in set(parking["park_name"]),
                "facilities": sum(
                    boundary.contains(_geometry_from_hex(row.geom))
                    for row in tables["nps_facilities"].itertuples(index=False)
                )
                > 0,
                "historic_sites": sum(
                    boundary.contains(_geometry_from_hex(row.geom))
                    for row in nrhp.itertuples(index=False)
                )
                > 0,
                "boundary": True,
            }
        )
    completeness = pd.DataFrame(completeness_rows)

    historic_site_density_rows = []
    for park_name, boundary in boundary_geoms.items():
        historic_count = sum(
            boundary.contains(_geometry_from_hex(row.geom)) for row in nrhp.itertuples(index=False)
        )
        if historic_count == 0:
            continue
        area_sq_km = float(areas.loc[areas["park_name"] == park_name, "area_sq_km"].iloc[0])
        historic_site_density_rows.append(
            {
                "park_name": park_name,
                "historic_site_records": historic_count,
                "historic_site_records_per_100_sq_km": historic_count / area_sq_km * 100,
            }
        )
    historic_site_density = pd.DataFrame(historic_site_density_rows).sort_values(
        "historic_site_records_per_100_sq_km", ascending=False
    )

    return {
        "seasonality": seasonality,
        "visitation_pressure": visitation_pressure.sort_values(
            "avg_annual_visitors_per_sq_km",
            ascending=False,
        ),
        "infrastructure_density": infrastructure_density.sort_values("park_name"),
        "completeness_matrix": completeness.sort_values("park_name"),
        "historic_site_density": historic_site_density.reset_index(drop=True),
    }


def write_query_results(tables: dict[str, pd.DataFrame], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    output_frames = {
        **original_query_results(tables),
        **advanced_analysis_results(tables),
    }
    for name, frame in output_frames.items():
        path = output_dir / f"{name}.csv"
        frame.to_csv(path, index=False)
        written.append(path)
    return written


def _plot_polygon(ax, geom, **kwargs) -> None:
    for polygon in geom.geoms if geom.geom_type == "MultiPolygon" else [geom]:
        x, y = polygon.exterior.xy
        ax.plot(x, y, **kwargs)


def _plot_lines(ax, geom, **kwargs) -> None:
    for line in geom.geoms if geom.geom_type == "MultiLineString" else [geom]:
        x, y = line.xy
        ax.plot(x, y, **kwargs)


def write_figures(tables: dict[str, pd.DataFrame], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    advanced = advanced_analysis_results(tables)

    seasonality = advanced["seasonality"]
    fig, ax = plt.subplots(figsize=(10, 6))
    x_positions = list(range(len(MONTH_ORDER)))
    for park_name, subset in seasonality.groupby("np_name"):
        ordered_subset = subset.set_index("month").reindex(MONTH_ORDER).reset_index()
        ax.plot(x_positions, ordered_subset["avg_monthly_visitors"], marker="o", label=park_name)
    ax.set_title("Average Monthly Visitation by Park")
    ax.set_ylabel("Average Monthly Visitors")
    ax.set_xlabel("Month")
    ax.set_xticks(x_positions, MONTH_ORDER, rotation=45)
    ax.legend()
    fig.tight_layout()
    path = output_dir / "visitation_seasonality.png"
    fig.savefig(path, dpi=200)
    written.append(path)
    plt.close(fig)

    pressure = advanced["visitation_pressure"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(pressure["park_name"], pressure["avg_annual_visitors_per_sq_km"], color="#4C7A54")
    ax.set_title("Average Annual Visitation Pressure (2010-2020)")
    ax.set_ylabel("Visitors per Square Kilometer")
    ax.set_xlabel("Park")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    path = output_dir / "visitation_pressure.png"
    fig.savefig(path, dpi=200)
    written.append(path)
    plt.close(fig)

    completeness = advanced["completeness_matrix"].copy()
    datasets = [
        "visitation",
        "roads",
        "trails",
        "parking",
        "facilities",
        "historic_sites",
        "boundary",
    ]
    matrix = completeness[datasets].astype(int).to_numpy()
    fig, ax = plt.subplots(figsize=(9, 4))
    image = ax.imshow(matrix, cmap="Greens", aspect="auto", vmin=0, vmax=1)
    ax.set_title("Recovered Data Completeness Matrix")
    ax.set_xticks(range(len(datasets)), datasets, rotation=30, ha="right")
    ax.set_yticks(range(len(completeness)), completeness["park_name"])
    fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02, label="Coverage")
    fig.tight_layout()
    path = output_dir / "data_completeness_heatmap.png"
    fig.savefig(path, dpi=200)
    written.append(path)
    plt.close(fig)

    boundaries = tables["nps_boundary"]
    trails = tables["park_trails"]
    parking = tables["parking_areas"]
    nrhp = tables["nrhp_points"]
    facilities = tables["nps_facilities"]
    rocky_boundary = _geometry_from_hex(
        boundaries.loc[boundaries["parkname"] == "Rocky Mountain", "geom"].iloc[0]
    )
    fig, ax = plt.subplots(figsize=(8, 12))
    _plot_polygon(ax, rocky_boundary, color="black", linewidth=1.2)
    for row in trails.loc[trails["park_name"] == "Rocky Mountain"].itertuples(index=False):
        _plot_lines(ax, _geometry_from_hex(row.geom), color="#9B8B5A", linewidth=0.6, alpha=0.7)
    campground_points = [
        _geometry_from_hex(row.geom)
        for row in facilities.itertuples(index=False)
        if row.facility_type == "Campground"
        and rocky_boundary.contains(_geometry_from_hex(row.geom))
    ]
    if campground_points:
        ax.scatter(
            [geom.x for geom in campground_points],
            [geom.y for geom in campground_points],
            marker="^",
            color="#4C8C4A",
            s=45,
            label="Campground",
        )
    parking_points = [
        _geometry_from_hex(row.geom)
        for row in parking.loc[parking["park_name"] == "Rocky Mountain"].itertuples(index=False)
    ]
    ax.scatter(
        [geom.x for geom in parking_points],
        [geom.y for geom in parking_points],
        marker="o",
        facecolors="none",
        edgecolors="#3C86C8",
        s=35,
        label="Parking area",
    )
    nrhp_points = [
        _geometry_from_hex(row.geom)
        for row in nrhp.itertuples(index=False)
        if rocky_boundary.contains(_geometry_from_hex(row.geom))
    ]
    ax.scatter(
        [geom.x for geom in nrhp_points],
        [geom.y for geom in nrhp_points],
        marker="o",
        color="#C73A3A",
        s=16,
        label="Historic site",
    )
    ax.set_title("Reconstructed Rocky Mountain Amenity Map")
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.legend(loc="lower right")
    fig.tight_layout()
    path = output_dir / "rocky_mountain_amenity_map.png"
    fig.savefig(path, dpi=200)
    written.append(path)
    plt.close(fig)

    return written


def run_analysis(dump_path: Path, write_figures_flag: bool = False) -> dict[str, list[Path] | Path]:
    paths = project_paths()
    tables = load_public_tables(dump_path)
    quality_path = paths.quality_reports_dir / "spatial_quality_summary.csv"
    reconciliation_path = paths.quality_reports_dir / "migration_reconciliation.csv"
    quality_path.parent.mkdir(parents=True, exist_ok=True)
    spatial_quality_summary(tables).to_csv(quality_path, index=False)
    write_migration_reconciliation(tables, reconciliation_path)
    query_paths = write_query_results(tables, paths.query_results_dir)
    figure_paths = write_figures(tables, paths.figures_dir) if write_figures_flag else []
    return {
        "quality_summary": quality_path,
        "migration_reconciliation": reconciliation_path,
        "query_results": query_paths,
        "figures": figure_paths,
    }
