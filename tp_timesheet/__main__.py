""" Entry point for cli """
import logging
import os
import sys
import argparse
import warnings
from workalendar.asia import Singapore
from tp_timesheet.docker_handler import DockerHandler
from tp_timesheet.submit_form import submit_timesheet
from tp_timesheet.date_utils import get_working_dates, get_start_date
from tp_timesheet.schedule import ScheduleForm
from tp_timesheet.config import Config

logger = logging.getLogger(__name__)


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


def run():
    """Entry point"""
    args = parse_args()

    config = Config(verbose=args.verbose)
    # Automate Mode
    if args.automate is not None:
        valid_options = ["weekdays"]
        if args.automate not in valid_options:
            logger.error(
                "'%s' is not a valid option for --automate mode", args.automate
            )
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
    dates = get_working_dates(start=start_date, count=args.count, cal=cal)

    if not dates:
        logger.info(
            "Submitted dates fall on weekends, form submission is not required."
        )
        return

    string_list = [f"{date}: {hours} hours" for (date, hours) in dates]
    logger.info(
        "Date(s) (yyyy-mm-dd) to be submitted for %s: %s", config.EMAIL, string_list
    )

    docker_handler = DockerHandler()
    try:
        logger.debug("Pulling latest image")
        docker_handler.pull_image()
        logger.debug("Launching docker container for selenium backend")
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
            if args.dry_run:
                notification_text = f"[DRY_RUN] {notification_text}"
            os.system(
                f"""osascript -e 'display notification "{notification_text}" with title "TP Timesheet"'"""
            )

    finally:
        logger.debug("Cleaning up docker container")
        if docker_handler.container is not None:
            docker_handler.rm_container()


if __name__ == "__main__":
    run()
