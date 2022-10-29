"""Unit tests for the date parsing method"""
import os
import sys
import builtins
from datetime import datetime, timedelta
import mock
from tp_timesheet.date_utils import get_start_date, assert_start_date
from tp_timesheet.config import Config

tests_path = os.path.dirname(os.path.abspath(__file__))
src_path = tests_path + "/../"
sys.path.insert(0, src_path)

# fmt: off
TEST_CASES_FORMATS_DMY = [
        # 4-digit year(%Y)
            # slashes
            '%d/%m/%Y', # "05/02/2022"
            '%-d/%-m/%Y', # "5/2/2022"
            '%d/%-m/%Y', # "05/2/2022"
            '%-d/%m/%Y', # "5/02/2022"
            # hyphens
            '%d-%m-%Y', # "05-02-2022"
            '%-d-%-m-%Y', # "5-2-2022"
            '%d-%-m-%Y', # "05-2-2022"
            '%-d-%m-%Y', # "5-02-2022"
            # spaces
            '%d %m %Y', # "05 02 2022"
            '%-d %-m %Y', # "5 2 2022"
            '%d %-m %Y', # "05 2 2022"
            '%-d %m %Y', # "5 02 2022"
        # 2-digit year(%y)
            # slashes
            '%d/%m/%y', # "05/02/22"
            '%-d/%-m/%y', # "5/2/22"
            '%d/%-m/%y', # "05/2/22"
            '%-d/%m/%y', # "5/02/22"
            # hyphens
            '%d-%m-%y', # "05-02-22"
            '%-d-%-m-%y', # "5-2-22"
            '%d-%-m-%y', # "05-2-22"
            '%-d-%m-%y', # "5-02-22"
            # spaces
            '%d %m %y', # "05 02 22"
            '%-d %-m %y', # "5 2 22"
            '%d %-m %y', # "05 2 22"
            '%-d %m %y', # "5 02 22"
]

TEST_CASES_FORMATS_YMD = [
        # 4-digit year(%Y)
            # slashes
            '%Y/%m/%d', # "2022/02/05"
            '%Y/%-m/%-d', # "2022/2/5"
            '%Y/%-m/%d', # "2022/2/05"
            '%Y/%m/%-d', # "2022/02/5"
            # hyphens
            '%Y-%m-%d', # "2022-02-05"
            '%Y-%-m-%-d', # "2022-2-5"
            '%Y-%-m-%d', # "2022-2-05"
            '%Y-%m-%-d', # "2022-02-5"
            # spaces
            '%Y %m %d', # "2022 02 05"
            '%Y %-m %-d', # "2022 2 5"
            '%Y %-m %d', # "2022 2 05"
            '%Y %m %-d', # "2022 02 5"
        # 2-digit year(%y)
            # slashes
            '%y/%m/%d', # "22/02/05"
            '%y/%-m/%-d', # "22/2/5"
            '%y/%-m/%d', # "22/2/05"
            '%y/%m/%-d', # "22/02/5"
            # hyphens
            '%y-%m-%d', # "22-02-05"
            '%y-%-m-%-d', # "22-2-5"
            '%y-%-m-%d', # "22-2-05"
            '%y-%m-%-d', # "22-02-5"
            # spaces
            '%y %m %d', # "22 02 05"
            '%y %-m %-d', # "22 2 5"
            '%y %-m %d', # "22 2 05"
            '%y %m %-d', # "22 02 5"
]
# fmt: on


def test_various_date_formats():
    """
    test variaous date formats
    formats : listed on TEST_CASES_FORMATS_DMY, TEST_CASES_FORMATS_YMD
    """
    # A range beyond 6 month is not supported by the current logic. for instance,
    # today : 2022-10-10 / target : 2023-4-22 / parsed : 2022-4-23
    days_span = 180
    today = datetime.today()
    for target_date in (
        today + timedelta(n) for n in range(-1 * days_span, days_span + 1)
    ):
        year, month, day = target_date.year, target_date.month, target_date.day
        for date_format in TEST_CASES_FORMATS_DMY + TEST_CASES_FORMATS_YMD:
            parsed = get_start_date(target_date.strftime(date_format))
            query_str = target_date.strftime(date_format)
            assert (
                parsed.year == year
            ), f"parsing error, query:{query_str} and parsed:{parsed}"
            assert (
                parsed.month == month
            ), f"parsing error, query:{query_str} and parsed:{parsed}"
            assert (
                parsed.day == day
            ), f"parsing error, query:{query_str} and parsed:{parsed}"


def test_assert_start_date():
    """
    test the assert function of start date
    """
    Config()
    Config.CHECK_MAX_DAYS = True

    testing_span = 2 * int(Config.MAX_DAYS)
    today = datetime.today().date()

    with mock.patch.object(builtins, "input", lambda _: "y"):
        for delta in range(-1 * testing_span, testing_span + 1):
            assertion_result = assert_start_date(today + timedelta(delta))
            assert assertion_result, "start date assertion failed"

    with mock.patch.object(builtins, "input", lambda _: "n"):
        for delta in range(-1 * testing_span, -1 * int(Config.MAX_DAYS)):
            assertion_result = assert_start_date(today + timedelta(delta))
            assert not assertion_result, "start date assertion failed"

        for delta in range(-1 * int(Config.MAX_DAYS), int(Config.MAX_DAYS) + 1):
            assertion_result = assert_start_date(today + timedelta(delta))
            assert assertion_result, "start date assertion failed"

        for delta in range(int(Config.MAX_DAYS) + 1, testing_span + 1):
            assertion_result = assert_start_date(today + timedelta(delta))
            assert not assertion_result, "start date assertion failed"
