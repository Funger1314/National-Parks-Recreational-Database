"""Validation utilities for reconstructed visitation data."""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pandas as pd

from national_parks.config import MONTH_ORDER, PARK_ALIAS_MAP, VISITATION_NUMERIC_COLUMNS


@dataclass(slots=True)
class ValidationArtifacts:
    frame: pd.DataFrame
    coercion_failures: pd.DataFrame
    duplicate_rows: pd.DataFrame
    quality_report: pd.DataFrame


def normalize_month_name(value: object) -> str:
    text = str(value).strip()
    month_map = {
        name.lower(): name
        for name in calendar.month_name
        if name
    }
    if text.lower() not in month_map:
        raise ValueError(f"Unrecognized month value: {value!r}")
    return month_map[text.lower()]


def standardize_park_name(value: object) -> str:
    text = str(value).strip()
    if text not in PARK_ALIAS_MAP:
        raise ValueError(f"Unexpected park name: {text!r}")
    return PARK_ALIAS_MAP[text]


def validate_expected_columns(frame: pd.DataFrame, expected: list[str]) -> None:
    missing = [column for column in expected if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def coerce_numeric_columns(
    frame: pd.DataFrame,
    columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    working = frame.copy()
    failures: list[dict[str, object]] = []
    for column in columns:
        stripped = working[column].astype(str).str.replace(",", "", regex=False).str.strip()
        coerced = pd.to_numeric(stripped, errors="coerce")
        failed_mask = coerced.isna() & stripped.ne("")
        for row_index in working.index[failed_mask]:
            failures.append(
                {
                    "row_index": int(row_index),
                    "column_name": column,
                    "raw_value": working.at[row_index, column],
                }
            )
        working[column] = coerced.astype("Int64")
    return working, pd.DataFrame(failures)


def validate_visitation_frame(
    frame: pd.DataFrame,
    expected_year_range: tuple[int, int] = (1979, 2021),
) -> ValidationArtifacts:
    working = frame.copy()
    working["month"] = working["month"].map(normalize_month_name)
    working["np_name"] = working["np_name"].map(standardize_park_name)

    numeric_frame, coercion_failures = coerce_numeric_columns(working, VISITATION_NUMERIC_COLUMNS)

    duplicate_rows = numeric_frame[
        numeric_frame.duplicated(subset=["np_name", "year", "month"], keep=False)
    ].copy()

    quality_rows = [
        {
            "check_name": "row_count",
            "status": "pass" if len(numeric_frame) > 0 else "fail",
            "value": len(numeric_frame),
            "notes": "Expected merged visitation rows should be deterministic.",
        },
        {
            "check_name": "coercion_failures",
            "status": "pass" if coercion_failures.empty else "fail",
            "value": len(coercion_failures),
            "notes": "Numeric coercion strips commas and reports non-numeric values.",
        },
        {
            "check_name": "duplicate_park_year_month",
            "status": "pass" if duplicate_rows.empty else "fail",
            "value": len(duplicate_rows),
            "notes": "Rows should be unique by park, year, and month.",
        },
        {
            "check_name": "valid_year_range",
            "status": "pass"
            if numeric_frame["year"].between(*expected_year_range).all()
            else "fail",
            "value": f"{numeric_frame['year'].min()}..{numeric_frame['year'].max()}",
            "notes": "Expected years follow the recovered 1979-2021 range.",
        },
        {
            "check_name": "valid_month_names",
            "status": "pass"
            if set(numeric_frame["month"].unique()).issubset(set(MONTH_ORDER))
            else "fail",
            "value": ", ".join(sorted(numeric_frame["month"].dropna().unique())),
            "notes": "Months are standardized to full English month names.",
        },
    ]

    for column in VISITATION_NUMERIC_COLUMNS:
        negative_count = int((numeric_frame[column] < 0).fillna(False).sum())
        quality_rows.append(
            {
                "check_name": f"nonnegative_{column}",
                "status": "pass" if negative_count == 0 else "fail",
                "value": negative_count,
                "notes": "Count metrics should not be negative.",
            }
        )

    return ValidationArtifacts(
        frame=numeric_frame,
        coercion_failures=coercion_failures,
        duplicate_rows=duplicate_rows,
        quality_report=pd.DataFrame(quality_rows),
    )
