"""Unit tests for the date parsing method"""
import pytest
import os
import sys
import datetime
import dateutil.parser
from tp_timesheet.__main__ import get_start_date

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


def test_varios_date_formats():
    today = datetime.datetime.today()
    year, month, day = today.year, today.month, today.day
    for date_format in TEST_CASES_FORMATS_DMY + TEST_CASES_FORMATS_YMD:
        parsed = get_start_date(today.strftime(date_format))
        assert (
            parsed.year == year
        ), f"parsing error, query:{today.strftime(date_format)} and parsed:{parsed}"
        assert (
            parsed.month == month
        ), f"parsing error, query:{today.strftime(date_format)} and parsed:{parsed}"
        assert (
            parsed.day == day
        ), f"parsing error, query:{today.strftime(date_format)} and parsed:{parsed}"
