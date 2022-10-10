""" Module containing methods to process `date` related """
import re
from datetime import datetime, timedelta
import dateutil.parser


def date_fn(start, count, cal):
    """get workdays from `start` date to `start+count` date"""
    dates = []
    for i in range(count):
        day = start + timedelta(days=i)
        day = day.date()
        year = day.year
        holidays = cal.holidays(year)
        holidates = [date for (date, _) in holidays]
        if day.isoweekday() < 6:
            if day not in holidates:
                dates.append((day, 8))
            else:
                dates.append((day, 0))
    return dates


def get_start_date(start_date_arg):
    """parse user's `start` argument"""
    if start_date_arg.lower() == "today":
        start_date = datetime.today()
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
