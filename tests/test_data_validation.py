import pandas as pd

from national_parks.validation import normalize_month_name, validate_visitation_frame


def test_normalize_month_name_handles_case_insensitive_values() -> None:
    assert normalize_month_name("january") == "January"
    assert normalize_month_name("October") == "October"


def test_validate_visitation_frame_reports_coercion_and_duplicates() -> None:
    frame = pd.DataFrame(
        [
            {
                "year": "1979",
                "month": "january",
                "recreation_visitors": "1,000",
                "non_recreation_visitors": "5",
                "recreation_hr": "1",
                "non_recreation_hr": "2",
                "concession_lodging": "3",
                "tent_campers": "4",
                "rv_campers": "5",
                "concession_camping": "6",
                "backcountry_campers": "7",
                "misc_campers": "8",
                "non_recreation_overnight_stays": "0",
                "total_overnight_stays": "9",
                "np_name": "Rocky Mountain",
            },
            {
                "year": "1979",
                "month": "January",
                "recreation_visitors": "not-a-number",
                "non_recreation_visitors": "5",
                "recreation_hr": "1",
                "non_recreation_hr": "2",
                "concession_lodging": "3",
                "tent_campers": "4",
                "rv_campers": "5",
                "concession_camping": "6",
                "backcountry_campers": "7",
                "misc_campers": "8",
                "non_recreation_overnight_stays": "0",
                "total_overnight_stays": "9",
                "np_name": "Rocky Mountain",
            },
        ]
    )

    result = validate_visitation_frame(frame)

    assert len(result.coercion_failures) == 1
    assert len(result.duplicate_rows) == 2
    assert result.frame.loc[0, "month"] == "January"

