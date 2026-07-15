from pathlib import Path

from national_parks.visitation_cleaning import process_raw_visitation_directory, read_visitation_csv


def _write_visitation_csv(path: Path, month_label: str) -> None:
    lines = [
        "metadata line 1",
        "metadata line 2",
        "metadata line 3",
        "Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9,Field10,Field11,Field12,Field13,Field14",
        f"1979,{month_label},1,2,3,4,5,6,7,8,9,10,0,11",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def test_read_visitation_csv_normalizes_generic_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "ROMO(1979-2021).csv"
    _write_visitation_csv(csv_path, "January")

    frame = read_visitation_csv(csv_path, park_name="Rocky Mountain")

    assert list(frame.columns) == [
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
    assert frame.loc[0, "np_name"] == "Rocky Mountain"


def test_process_raw_visitation_directory_merges_expected_files(tmp_path: Path) -> None:
    for abbreviation, month_name in {
        "ROMO": "January",
        "GRSM": "February",
        "GRTE": "March",
        "ASIS": "April",
    }.items():
        _write_visitation_csv(tmp_path / f"{abbreviation}(1979-2021).csv", month_name)

    output_csv = tmp_path / "processed.csv"
    quality_csv = tmp_path / "quality.csv"
    result = process_raw_visitation_directory(tmp_path, output_csv, quality_csv)

    assert len(result.frame) == 4
    assert output_csv.exists()
    assert quality_csv.exists()
    assert set(result.frame["np_name"]) == {
        "Rocky Mountain",
        "Great Smoky Mountain",
        "Grand Teton",
        "Assateague Island",
    }
