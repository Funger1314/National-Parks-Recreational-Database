import os
import shutil
import subprocess

import pytest


@pytest.mark.skipif(
    not os.getenv("POSTGRES_DSN") or shutil.which("psql") is None,
    reason="POSTGRES_DSN or psql is unavailable",
)
def test_core_schema_exists() -> None:
    result = subprocess.run(
        ["psql", os.environ["POSTGRES_DSN"], "-Atc", "SELECT to_regnamespace('core') IS NOT NULL;"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "t"

