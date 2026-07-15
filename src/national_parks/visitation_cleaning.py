"""Visitation ETL reconstruction based on the original report."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from national_parks.config import (
    PARK_ABBREVIATIONS,
    VISITATION_COLUMN_SYNONYMS,
    VISITATION_FINAL_COLUMNS,
)
from national_parks.database import export_table_to_csv
from national_parks.validation import (
    ValidationArtifacts,
    validate_expected_columns,
    validate_visitation_frame,
)

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class VisitationWorkflowResult:
    frame: pd.DataFrame
    validation: ValidationArtifacts


def _rename_columns(frame: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        column: VISITATION_COLUMN_SYNONYMS[column]
        for column in frame.columns
        if column in VISITATION_COLUMN_SYNONYMS
    }
    renamed = frame.rename(columns=rename_map)
    return renamed


def read_visitation_csv(
    csv_path: Path,
    park_name: str,
    skiprows: int = 3,
) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Visitation CSV not found: {csv_path}")

    frame = pd.read_csv(csv_path, skiprows=skiprows, dtype=str)
    frame = _rename_columns(frame)
    frame["np_name"] = park_name

    validate_expected_columns(frame, VISITATION_FINAL_COLUMNS)
    return frame[VISITATION_FINAL_COLUMNS]


def merge_visitation_files(input_dir: Path) -> VisitationWorkflowResult:
    frames: list[pd.DataFrame] = []
    for abbreviation, park_name in PARK_ABBREVIATIONS.items():
        matches = sorted(input_dir.glob(f"{abbreviation}*.csv"))
        if not matches:
            raise FileNotFoundError(
                f"No visitation CSV matching {abbreviation}*.csv was found in {input_dir}"
            )
        LOGGER.info("Reading %s for %s", matches[0].name, park_name)
        frames.append(read_visitation_csv(matches[0], park_name=park_name))

    merged = pd.concat(frames, ignore_index=True)
    validation = validate_visitation_frame(merged)
    return VisitationWorkflowResult(frame=validation.frame, validation=validation)


def process_raw_visitation_directory(
    input_dir: Path,
    output_csv: Path,
    output_quality_report: Path,
) -> VisitationWorkflowResult:
    result = merge_visitation_files(input_dir=input_dir)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_quality_report.parent.mkdir(parents=True, exist_ok=True)
    result.frame.to_csv(output_csv, index=False)
    result.validation.quality_report.to_csv(output_quality_report, index=False)
    if not result.validation.coercion_failures.empty:
        result.validation.coercion_failures.to_csv(
            output_quality_report.with_name("visitation_coercion_failures.csv"),
            index=False,
        )
    return result


def export_recovered_visitation(dump_path: Path, output_csv: Path) -> Path:
    LOGGER.info("Exporting recovered np_visitation table from %s", dump_path)
    return export_table_to_csv(dump_path, "public", "np_visitation", output_csv)
