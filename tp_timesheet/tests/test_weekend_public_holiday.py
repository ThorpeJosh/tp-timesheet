"""Unit tests for the date parsing method"""
from datetime import date
from workalendar.asia import Singapore
from tp_timesheet.date_utils import get_working_dates

cal = Singapore()

# fmt: off
TEST_CASES = [
    # pylint: disable=line-too-long
    (date(2022, 1, 10), 1, [(date(2022, 1, 10), 8)]),  # weekday
    (date(2022, 1, 10), 3, [(date(2022, 1, 10), 8), (date(2022, 1, 11), 8), (date(2022, 1, 12), 8)]),  # consecutive weekdays
    (date(2022, 1, 1), 1, []),  # weekend
    (date(2022, 1, 1), 2, []),  # consecutive weekends
    (date(2022, 8, 9), 1, [(date(2022, 8, 9), 0)]),  # holiday
    (date(2022, 2, 1), 2, [(date(2022, 2, 1), 0), (date(2022, 2, 2), 0)]),  # consecutive holidays
    (date(2022, 2, 11), 4, [(date(2022, 2, 11), 8), (date(2022, 2, 14), 8)]),  # weekday wrapping weekend
    (date(2022, 8, 8), 3, [(date(2022, 8, 8), 8), (date(2022, 8, 9), 0), (date(2022, 8, 10), 8)]),  # weekdays wrapping holiday
    (date(2022, 4, 14), 5, [(date(2022, 4, 14), 8), (date(2022, 4, 15), 0), (date(2022, 4, 18), 8)]),  # weekday wrapping holiday and weekends
    (date(2022, 4, 15), 2, [(date(2022, 4, 15), 0)]),  # holiday to weekend
    # pylint: enable=line-too-long
]
# fmt: on


def test_working_dates():
    """
    test dates account for weekends and holidays correctly
    """
    for start_date, count, expected_result in TEST_CASES:
        res = get_working_dates(start_date, count, cal, working_hours=8)
        assert (
            res == expected_result
        ), f"Error, expected: {expected_result}, result:{res}"
