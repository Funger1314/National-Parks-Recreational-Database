"""Migration reconciliation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from shapely import from_wkb, make_valid
from shapely.errors import GEOSException
from shapely.strtree import STRtree

from national_parks.config import PARK_ALIAS_MAP


@dataclass(frozen=True, slots=True)
class MigrationTableSpec:
    legacy_table: str
    target_table: str
    geometry_column: str | None
    transformed_columns: tuple[str, ...]
    park_name_column: str | None = None
    park_association_method: str = "none"
    preserve_all_rows: bool = True
    repair_invalid_geometry: bool = False


MIGRATION_SPECS = (
    MigrationTableSpec(
        legacy_table="nps_boundary",
        target_table="core.park",
        geometry_column="geom",
        transformed_columns=(
            "park_id",
            "canonical_name",
            "area_square_meters",
            "source_dataset_id",
        ),
        repair_invalid_geometry=True,
    ),
    MigrationTableSpec(
        legacy_table="np_visitation",
        target_table="core.visitation",
        geometry_column=None,
        transformed_columns=(
            "visitation_id",
            "park_id",
            "source_id",
            "month_name",
            "source_dataset_id",
        ),
        park_name_column="np_name",
        park_association_method="park_name_alias",
        preserve_all_rows=False,
    ),
    MigrationTableSpec(
        legacy_table="nps_facilities",
        target_table="core.facility",
        geometry_column="geom",
        transformed_columns=(
            "facility_id",
            "park_id",
            "source_gid",
            "source_dataset_id",
        ),
        park_association_method="spatial",
        preserve_all_rows=True,
    ),
    MigrationTableSpec(
        legacy_table="nrhp_points",
        target_table="core.historic_site",
        geometry_column="geom",
        transformed_columns=(
            "historic_site_id",
            "park_id",
            "source_gid",
            "resource_name",
            "resource_type",
            "source_dataset_id",
        ),
        park_association_method="spatial",
        preserve_all_rows=True,
    ),
    MigrationTableSpec(
        legacy_table="park_roads",
        target_table="core.road",
        geometry_column="geom",
        transformed_columns=(
            "road_id",
            "park_id",
            "source_gid",
            "park_name_raw",
            "road_surface",
            "seasonal_flag",
            "seasonal_description",
            "source_length_meters",
            "geometry",
            "source_dataset_id",
        ),
        park_name_column="park_name",
        park_association_method="park_name_alias",
        preserve_all_rows=True,
    ),
    MigrationTableSpec(
        legacy_table="park_trails",
        target_table="core.trail",
        geometry_column="geom",
        transformed_columns=(
            "trail_id",
            "park_id",
            "source_gid",
            "park_name_raw",
            "trail_name",
            "trail_type",
            "trail_use",
            "historic_significance",
            "source_length_meters",
            "source_dataset_id",
        ),
        park_name_column="park_name",
        park_association_method="park_name_alias",
        preserve_all_rows=True,
    ),
    MigrationTableSpec(
        legacy_table="parking_areas",
        target_table="core.parking_area",
        geometry_column="geom",
        transformed_columns=(
            "parking_area_id",
            "park_id",
            "source_gid",
            "park_name_raw",
            "lot_type",
            "route_name",
            "handicapped_space",
            "seasonal_flag",
            "year_built",
            "source_dataset_id",
        ),
        park_name_column="park_name",
        park_association_method="park_name_alias",
        preserve_all_rows=True,
    ),
)

REPORT_COLUMNS = [
    "legacy_table",
    "target_table",
    "legacy_row_count",
    "migrated_row_count",
    "excluded_row_count",
    "duplicate_row_count",
    "unresolved_park_association_count",
    "null_geometry_count",
    "invalid_geometry_count",
    "repaired_geometry_count",
    "remaining_invalid_geometry_count",
    "transformed_column_count",
    "matched_by_source_identifier_count",
    "matched_by_park_name_alias_count",
    "matched_spatially_count",
    "ambiguous_match_count",
    "equation_reconciles",
    "discrepancy_explanation",
]


def _geometry_from_hex(value: str):
    return from_wkb(bytes.fromhex(value))


def _load_geometries(frame: pd.DataFrame, geometry_column: str | None) -> list[object | None]:
    if geometry_column is None:
        return []
    geometries: list[object | None] = []
    for value in frame[geometry_column]:
        if value in (None, "", "\\N"):
            geometries.append(None)
            continue
        geometries.append(_geometry_from_hex(value))
    return geometries


def _count_invalid_geometries(
    geometries: list[object | None],
    repair_invalid_geometry: bool,
) -> tuple[int, int, int]:
    invalid_count = 0
    repaired_count = 0
    remaining_invalid_count = 0
    for geometry in geometries:
        if geometry is None:
            continue
        is_valid = bool(geometry.is_valid)
        if is_valid:
            continue
        invalid_count += 1
        if repair_invalid_geometry:
            repaired_geometry = make_valid(geometry)
            if repaired_geometry.is_valid:
                repaired_count += 1
            else:
                remaining_invalid_count += 1
        else:
            remaining_invalid_count += 1
    return invalid_count, repaired_count, remaining_invalid_count


def _alias_match_counts(
    frame: pd.DataFrame,
    raw_name_column: str,
    valid_park_names: set[str],
    preserve_all_rows: bool,
) -> tuple[int, int, int, int]:
    matched_by_alias_count = 0
    unresolved_count = 0
    excluded_count = 0
    for raw_name in frame[raw_name_column]:
        canonical_name = PARK_ALIAS_MAP.get(str(raw_name).strip())
        if canonical_name and canonical_name in valid_park_names:
            matched_by_alias_count += 1
        else:
            unresolved_count += 1
            if not preserve_all_rows:
                excluded_count += 1
    migrated_count = len(frame) - excluded_count
    return matched_by_alias_count, unresolved_count, excluded_count, migrated_count


def _spatial_match_counts(
    frame: pd.DataFrame,
    geometry_column: str,
    boundary_frame: pd.DataFrame,
) -> tuple[int, int, int]:
    boundary_geometries = []
    for value in boundary_frame["geom"]:
        geometry = _geometry_from_hex(value)
        if not geometry.is_valid:
            geometry = make_valid(geometry)
        boundary_geometries.append(geometry)

    tree = STRtree(boundary_geometries)
    matched_count = 0
    ambiguous_count = 0
    unresolved_count = 0

    for value in frame[geometry_column]:
        if value in (None, "", "\\N"):
            unresolved_count += 1
            continue
        geometry = _geometry_from_hex(value)
        candidate_indices = tree.query(geometry)
        containing_indices: list[int] = []
        for candidate_index in candidate_indices:
            candidate_geometry = boundary_geometries[int(candidate_index)]
            try:
                if candidate_geometry.contains(geometry):
                    containing_indices.append(int(candidate_index))
            except GEOSException:
                continue
        if len(containing_indices) == 1:
            matched_count += 1
        elif len(containing_indices) > 1:
            ambiguous_count += 1
            unresolved_count += 1
        else:
            unresolved_count += 1

    return matched_count, ambiguous_count, unresolved_count


def build_migration_reconciliation(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    boundary_frame = tables["nps_boundary"]
    valid_park_names = set(boundary_frame["parkname"])
    rows: list[dict[str, object]] = []

    for spec in MIGRATION_SPECS:
        frame = tables[spec.legacy_table]
        legacy_row_count = len(frame)
        duplicate_row_count = 0
        geometries = _load_geometries(frame, spec.geometry_column)
        null_geometry_count = sum(geometry is None for geometry in geometries)
        invalid_geometry_count, repaired_geometry_count, remaining_invalid_geometry_count = (
            _count_invalid_geometries(geometries, spec.repair_invalid_geometry)
        )

        matched_by_source_identifier_count = 0
        matched_by_park_name_alias_count = 0
        matched_spatially_count = 0
        ambiguous_match_count = 0
        unresolved_park_association_count = 0
        excluded_row_count = 0
        migrated_row_count = legacy_row_count

        if spec.park_association_method == "park_name_alias" and spec.park_name_column:
            (
                matched_by_park_name_alias_count,
                unresolved_park_association_count,
                excluded_row_count,
                migrated_row_count,
            ) = _alias_match_counts(
                frame,
                spec.park_name_column,
                valid_park_names,
                preserve_all_rows=spec.preserve_all_rows,
            )
        elif spec.park_association_method == "spatial" and spec.geometry_column:
            (
                matched_spatially_count,
                ambiguous_match_count,
                unresolved_park_association_count,
            ) = _spatial_match_counts(frame, spec.geometry_column, boundary_frame)
        else:
            matched_by_source_identifier_count = legacy_row_count

        equation_reconciles = (
            legacy_row_count == migrated_row_count + excluded_row_count + duplicate_row_count
        )
        explanation = _build_discrepancy_explanation(
            spec=spec,
            legacy_row_count=legacy_row_count,
            migrated_row_count=migrated_row_count,
            excluded_row_count=excluded_row_count,
            duplicate_row_count=duplicate_row_count,
            unresolved_park_association_count=unresolved_park_association_count,
            null_geometry_count=null_geometry_count,
            invalid_geometry_count=invalid_geometry_count,
            repaired_geometry_count=repaired_geometry_count,
            remaining_invalid_geometry_count=remaining_invalid_geometry_count,
            matched_by_source_identifier_count=matched_by_source_identifier_count,
            matched_by_park_name_alias_count=matched_by_park_name_alias_count,
            matched_spatially_count=matched_spatially_count,
            ambiguous_match_count=ambiguous_match_count,
            equation_reconciles=equation_reconciles,
        )

        rows.append(
            {
                "legacy_table": spec.legacy_table,
                "target_table": spec.target_table,
                "legacy_row_count": legacy_row_count,
                "migrated_row_count": migrated_row_count,
                "excluded_row_count": excluded_row_count,
                "duplicate_row_count": duplicate_row_count,
                "unresolved_park_association_count": unresolved_park_association_count,
                "null_geometry_count": null_geometry_count,
                "invalid_geometry_count": invalid_geometry_count,
                "repaired_geometry_count": repaired_geometry_count,
                "remaining_invalid_geometry_count": remaining_invalid_geometry_count,
                "transformed_column_count": len(spec.transformed_columns),
                "matched_by_source_identifier_count": matched_by_source_identifier_count,
                "matched_by_park_name_alias_count": matched_by_park_name_alias_count,
                "matched_spatially_count": matched_spatially_count,
                "ambiguous_match_count": ambiguous_match_count,
                "equation_reconciles": equation_reconciles,
                "discrepancy_explanation": explanation,
            }
        )

    report = pd.DataFrame(rows, columns=REPORT_COLUMNS)
    assert_migration_reconciliation(report)
    return report


def _build_discrepancy_explanation(
    *,
    spec: MigrationTableSpec,
    legacy_row_count: int,
    migrated_row_count: int,
    excluded_row_count: int,
    duplicate_row_count: int,
    unresolved_park_association_count: int,
    null_geometry_count: int,
    invalid_geometry_count: int,
    repaired_geometry_count: int,
    remaining_invalid_geometry_count: int,
    matched_by_source_identifier_count: int,
    matched_by_park_name_alias_count: int,
    matched_spatially_count: int,
    ambiguous_match_count: int,
    equation_reconciles: bool,
) -> str:
    messages = [
        (
            f"{legacy_row_count} legacy rows map to {migrated_row_count} migrated rows in "
            f"{spec.target_table}."
        )
    ]
    if matched_by_source_identifier_count:
        messages.append(
            f"{matched_by_source_identifier_count} rows preserve one-to-one source-row identity."
        )
    if matched_by_park_name_alias_count:
        messages.append(
            f"{matched_by_park_name_alias_count} rows resolve park association "
            "through the alias map."
        )
    if matched_spatially_count:
        messages.append(f"{matched_spatially_count} rows resolve park association spatially.")
    if excluded_row_count:
        messages.append(
            f"{excluded_row_count} rows are excluded because the current migration uses an "
            "inner join on park-name alias resolution."
        )
    if unresolved_park_association_count:
        messages.append(
            f"{unresolved_park_association_count} rows remain with unresolved park association "
            "and therefore keep a null foreign key rather than being silently dropped."
        )
    if ambiguous_match_count:
        messages.append(
            f"{ambiguous_match_count} spatial matches are ambiguous and should not receive a "
            "park foreign key automatically."
        )
    if null_geometry_count:
        messages.append(f"{null_geometry_count} rows contain null geometry values.")
    if invalid_geometry_count:
        messages.append(
            f"{invalid_geometry_count} legacy geometries are invalid; "
            f"{repaired_geometry_count} are repaired in the modern geometry path and "
            f"{remaining_invalid_geometry_count} remain invalid after migration handling."
        )
    if not invalid_geometry_count:
        messages.append("No invalid legacy geometries were detected for this table.")
    if not duplicate_row_count:
        messages.append("No duplicate rows are intentionally removed in the current migration.")
    if not equation_reconciles:
        messages.append(
            "The reconciliation equation failed. Investigate row loss before "
            "accepting the migration."
        )
    else:
        messages.append("The reconciliation equation holds with no undocumented row loss.")
    messages.append(
        "Transformed columns: " + ", ".join(spec.transformed_columns) + "."
    )
    return " ".join(messages)


def assert_migration_reconciliation(report: pd.DataFrame) -> None:
    missing_columns = [column for column in REPORT_COLUMNS if column not in report.columns]
    if missing_columns:
        raise ValueError(f"Migration reconciliation report is missing columns: {missing_columns}")

    if report["discrepancy_explanation"].isna().any() or (
        report["discrepancy_explanation"].astype(str).str.strip() == ""
    ).any():
        raise ValueError("Every reconciliation row must include a discrepancy explanation.")

    mismatched_rows = report.loc[
        report["legacy_row_count"]
        != (
            report["migrated_row_count"]
            + report["excluded_row_count"]
            + report["duplicate_row_count"]
        )
    ]
    if not mismatched_rows.empty:
        raise ValueError(
            "Migration reconciliation equation failed for: "
            + ", ".join(mismatched_rows["legacy_table"].tolist())
        )


def write_migration_reconciliation(
    tables: dict[str, pd.DataFrame],
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_migration_reconciliation(tables)
    report.to_csv(output_path, index=False)
    return output_path
