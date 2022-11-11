""" Module containing methods to process `date` related """
import re
from typing import List, Tuple
import datetime
from datetime import datetime, timedelta
import dateutil.parser
from tp_timesheet.config import Config


def get_working_dates(
    start: datetime.date, count: int, cal, working_hours: int
) -> List[Tuple[datetime.date, int]]:
    """get workdays from `start` date to `start+count` date"""
    working_dates = []
    for i in range(count):
        current_date = start + timedelta(days=i)
        year = current_date.year
        holidays = cal.holidays(year)
        holidates = [date for (date, _) in holidays]
        if current_date.isoweekday() < 6:
            if current_date not in holidates:
                working_dates.append((current_date, working_hours))
            else:
                working_dates.append((current_date, 0))  # 0: number of working hours
    return working_dates


def get_start_date(start_date_arg: str) -> datetime.date:
    """parse user's `start` argument"""
    if start_date_arg.lower() == "today":
        start_date = datetime.today().date()
    elif start_date_arg.lower() == "yesterday":
        start_date = datetime.today().date() - timedelta(days=1)
    else:
        # PR#22 Parsing Dates with dateutil
        numbers = re.split("[-/ ]", start_date_arg)
        # 4 Digit Year
        if max(map(len, numbers)) == 4:
            yearfirst = len(numbers[0]) == 4
            dayfirst = not yearfirst
            start_date = dateutil.parser.parse(
                start_date_arg, yearfirst=yearfirst, dayfirst=dayfirst
            ).date()
        # 2 Digit Year
        else:
            cand1 = dateutil.parser.parse(start_date_arg, dayfirst=True).date()  # DMY
            cand2 = dateutil.parser.parse(start_date_arg, yearfirst=True).date()  # YMD
            today = datetime.today().date()
            diff1 = abs((cand1 - today).total_seconds())
            diff2 = abs((cand2 - today).total_seconds())
            # Select Nearest
            if diff1 < diff2:
                start_date = cand1
            else:
                start_date = cand2
    return start_date


def assert_start_date(start_date: datetime.date) -> bool:
    """
    check the start date submitting is bounded within `n` days.
    parse `n` from config file. default : 7

    Returns:
        True: when date is ok or verified by user as ok
        False: when date is invalid and confirmed by user as invalid
    """
    start_date_str = start_date.strftime("%d/%m/%Y")
    today = datetime.today().date()
    if (
        Config.SANITY_CHECK_START_DATE
        and int(Config.SANITY_CHECK_RANGE) < abs(today - start_date).days
    ):
        user_confirm = input(
            f"The entered date '{start_date_str}' "
            f"is beyond the maximum '{Config.SANITY_CHECK_RANGE}' day window from today.\n"
            f"You can modify the threshold and/or disable this confirmation option from '{Config.CONFIG_PATH}'.\n"
            f" - To modify threshold, change value of '{next(iter(Config.sanity_check_range_dict))}'.\n"
            f" - To disable, pass 'False' to '{next(iter(Config.sanity_check_bool_dict))}'.\n"
            f"Do you want to submit the timesheet anyway? [y/N]: "
        )
        if user_confirm.lower() != "y":
            return False
    return True
