import os
from pathlib import Path

import pytest

from national_parks.analysis import load_public_tables, original_query_results


@pytest.mark.skipif(not os.getenv("LEGACY_DUMP_PATH"), reason="LEGACY_DUMP_PATH is not set")
def test_original_query_outputs_match_verified_recovered_values() -> None:
    tables = load_public_tables(Path(os.environ["LEGACY_DUMP_PATH"]))
    outputs = original_query_results(tables)

    q3 = outputs["q3_rocky_mountain_amenity_counts"].iloc[0]
    assert int(q3["campground_records"]) == 7
    assert int(q3["nrhp_records"]) == 25
    assert int(q3["parking_records"]) == 133

