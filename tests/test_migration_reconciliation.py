import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from national_parks.analysis import load_public_tables
from national_parks.migration import (
    _load_geometries,
    assert_migration_reconciliation,
    build_migration_reconciliation,
)


def test_generated_migration_reconciliation_report_balances() -> None:
    report_path = Path("outputs/quality_reports/migration_reconciliation.csv")
    assert report_path.exists(), "migration_reconciliation.csv must be generated"

    report = pd.read_csv(report_path)
    assert_migration_reconciliation(report)

    required_columns = {
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
        "transformed_column_count",
        "discrepancy_explanation",
    }
    assert required_columns.issubset(report.columns)


def test_non_spatial_tables_do_not_report_null_geometry_by_default() -> None:
    frame = pd.DataFrame({"np_name": ["Acadia", "Yellowstone"]})
    assert _load_geometries(frame, None) == []


@pytest.mark.skipif(
    not os.getenv("POSTGRES_DSN") or shutil.which("psql") is None,
    reason="POSTGRES_DSN or psql is unavailable",
)
def test_visitation_row_counts_reconcile_after_migration() -> None:
    sql = """
    SELECT
        (SELECT COUNT(*) FROM legacy.np_visitation) =
        (SELECT COUNT(*) FROM core.visitation);
    """
    result = subprocess.run(
        ["psql", os.environ["POSTGRES_DSN"], "-Atc", sql],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "t"


@pytest.mark.skipif(not os.getenv("LEGACY_DUMP_PATH"), reason="LEGACY_DUMP_PATH is not set")
def test_recomputed_reconciliation_report_balances() -> None:
    tables = load_public_tables(Path(os.environ["LEGACY_DUMP_PATH"]))
    report = build_migration_reconciliation(tables)
    assert_migration_reconciliation(report)
