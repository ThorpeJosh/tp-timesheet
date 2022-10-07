""" Entry point for cli """
import os
import re
import sys
import argparse
import warnings
from datetime import datetime
import dateutil.parser
from workalendar.asia import Singapore
from tp_timesheet.docker_handler import DockerHandler
from tp_timesheet.submit_form import submit_timesheet
from tp_timesheet.dates import date_fn
from tp_timesheet.schedule import ScheduleForm
from tp_timesheet.config import Config


def parse_args():
    """Parse arguments from the command line"""
    parser = argparse.ArgumentParser(
        description="TP Automated Timesheet Submission - CLI Tool"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-s",
        "--start",
        type=str,
        help="Normal mode: Indicating first date to submit a timesheet. \
                Accepted arguments = ['Day/Month/Year', 'Day/Month/Year', today]. \
                NOTE: 'Month/Day/Year' is not accepted!",
    )
    group.add_argument(
        "-a",
        "--automate",
        type=str,
        help="Automate mode: Schedules the form submission to run automatically. Accepted arguments = [weekdays]",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        required=False,
        default=1,
        help="Number of weekdays to submit a timesheet for, use '5' on a monday to submit for the entire week",
    )
    parser.add_argument(
        "-n",
        "--notification",
        action="store_true",
        help="Notification feature, notification will be shown when the timesheet submission is done(for OSX only)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode, prints logs and saves screenshots of the timesheet submission page to your desktop",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry run mode, runs through as per normal but will not click submit",
    )
    return parser.parse_args()


def get_start_date(start_date_arg):
    """parse user's `start` argument"""
    if start_date_arg.lower() == "today":
        start_date = datetime.today()
    else:
        # PR#22 Parsing Dates with dateutil
        numbers = re.split("[-/ ]", start_date_arg)
        # 4 Digit Year
        if max(map(len, numbers)) == 4:
            start_date = dateutil.parser.parse(start_date_arg)
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


def run():
    """Entry point"""
    args = parse_args()
    config = Config()
    # Automate Mode
    if args.automate is not None:
        valid_options = ["weekdays"]
        if args.automate not in valid_options:
            print(f"'{args.automate}' is not a valid option for --automate mode")
            return
        scheduler = ScheduleForm()
        scheduler.schedule()
        return

    # Normal Mode
    if not args.verbose:
        warnings.filterwarnings(
            "ignore", message="Please take note that, due to arbitrary decisions, "
        )
    cal = Singapore()

    start_date = get_start_date(args.start)
    dates = date_fn(start=start_date, count=args.count, cal=cal)
    print(f"Date(s) (yyyy-mm-dd) to be submitted for {config.EMAIL}:")
    string_list = [f"{date}: {hours} hours" for (date, hours) in dates]
    print(string_list)

    docker_handler = DockerHandler()
    try:
        if args.verbose:
            print("Pulling latest image")
        docker_handler.pull_image()
        if args.verbose:
            print("Launching docker container for selenium backend")
        docker_handler.run_container()

        for (date, hours) in dates:
            submit_timesheet(
                config.URL,
                config.EMAIL,
                date,
                verbose=args.verbose,
                dry_run=args.dry_run,
                working_hours=hours,
            )

        # Notification (OSX only)
        if args.notification and sys.platform.lower() == "darwin":
            if len(dates) == 1:
                notification_text = (
                    f"Timesheet for {args.start.lower()} is successfully submitted."
                )
            else:
                notification_text = f"Timesheets from {dates[0]} to {dates[-1]} are successfully submitted."
            os.system(
                f"""osascript -e 'display notification "{notification_text}" with title "TP Timesheet"'"""
            )

    finally:
        if args.verbose:
            print("Cleaning up docker container")
        if docker_handler.container is not None:
            docker_handler.rm_container()


if __name__ == "__main__":
    run()
