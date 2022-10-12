""" Module containing methods to process `date` related """
import re
import sys
from datetime import datetime, timedelta
import dateutil.parser
from tp_timesheet.config import Config


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


def check_date(start_date):
    """
    check the start date submitting is bounded within `n` days.
    parse `n` from config file. default : 7
    """
    start_date_str = start_date.strftime("%d/%m/%Y")
    config = Config()
    today = datetime.today()
    if int(config.MAX_DAYS) < abs(today - start_date).days:
        user_confirm = input(
            f"The start date you process is '{start_date_str}' "
            f"and submitting beyond '{config.MAX_DAYS}' day is not recommended.\n"
            "You can modify the threshold and/or disable this confirmation option from '{config.CONFIG_PATH}'.\n"
            f"Do you want to submit the timesheet of the date?[y/N]: "
        )
        if user_confirm.lower() != "y":
            print("Aborted. Please re-start the program and pass new dates to process.")
            sys.exit()
