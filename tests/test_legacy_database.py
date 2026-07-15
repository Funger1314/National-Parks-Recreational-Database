import os
from pathlib import Path

import pytest

from national_parks.database import load_legacy_dump, table_to_dataframe


@pytest.mark.skipif(not os.getenv("LEGACY_DUMP_PATH"), reason="LEGACY_DUMP_PATH is not set")
def test_legacy_dump_core_table_counts() -> None:
    dump_path = Path(os.environ["LEGACY_DUMP_PATH"])
    dump = load_legacy_dump(dump_path)

    assert len(table_to_dataframe(dump, "public", "np_visitation")) == 2064
    assert len(table_to_dataframe(dump, "public", "nps_boundary")) == 72
    assert len(table_to_dataframe(dump, "public", "nps_facilities")) == 21904

