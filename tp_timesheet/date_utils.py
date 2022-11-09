""" Module containing methods to process `date` related """
import re
from typing import List, Tuple
from datetime import datetime, timedelta
import dateutil.parser


def get_working_dates(
    start: datetime, count: int, cal, working_hours: int
) -> List[Tuple[datetime, int]]:
    """get workdays from `start` date to `start+count` date"""
    working_dates = []
    for i in range(count):
        current_date = start + timedelta(days=i)
        current_date = current_date.date()
        year = current_date.year
        holidays = cal.holidays(year)
        holidates = [date for (date, _) in holidays]
        if current_date.isoweekday() < 6:
            if current_date not in holidates:
                working_dates.append((current_date, working_hours))
            else:
                working_dates.append((current_date, 0))  # 0: number of working hours
    return working_dates


def get_start_date(start_date_arg: str) -> datetime:
    """parse user's `start` argument"""
    if start_date_arg.lower() == "today":
        start_date = datetime.today()
    elif start_date_arg.lower() == "yesterday":
        start_date = datetime.today() - timedelta(days=1)
    else:
        # PR#22 Parsing Dates with dateutil
        numbers = re.split("[-/ ]", start_date_arg)
        # 4 Digit Year
        if max(map(len, numbers)) == 4:
            yearfirst = len(numbers[0]) == 4
            dayfirst = not yearfirst
            start_date = dateutil.parser.parse(
                start_date_arg, yearfirst=yearfirst, dayfirst=dayfirst
            )
        # 2 Digit Year
        else:
            cand1 = dateutil.parser.parse(start_date_arg, dayfirst=True)  # DMY
            cand2 = dateutil.parser.parse(start_date_arg, yearfirst=True)  # YMD
            today = datetime.today()
            diff1 = abs((cand1 - today).total_seconds())
            diff2 = abs((cand2 - today).total_seconds())
            # Select Nearest
            if diff1 < diff2:
                start_date = cand1
            else:
                start_date = cand2
    return start_date
