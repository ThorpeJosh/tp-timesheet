""" Entry point for cli """
import logging
import os
import sys
import argparse
import warnings
from workalendar.asia import Singapore
from tp_timesheet import __version__
from tp_timesheet.date_utils import get_working_dates, get_start_date, assert_start_date
from tp_timesheet.schedule import ScheduleForm
from tp_timesheet.config import Config
from tp_timesheet.clockify_timesheet import Clockify

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
                Accepted arguments = ['Day/Month/Year', 'Day/Month/Year', today, yesterday]. \
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
        help="Dry run mode, runs through as per normal but will not submit",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-t",
        "--task",
        action="append",
        nargs=2,
        metavar=("task", "hour"),
        help="The type of task for the clockify submission. Specify task name "
        + "if it is anything other than 'live'. Put the task name(idle, training, issue, OOO, holiday).\n"
        + 'Passing multiple task-hour pair is also acceptable. (E.g. "--task live 4 --task OOO 4" for afternoon OOO.)',
    )
    args = parser.parse_args()

    # postprocessing args
    logger.debug("Given task and hour pairs : %s", args.task)
    args.task = [["live", "8"]] if not args.task else args.task  # default value
    args.task = {task_name: int(hours) for (task_name, hours) in args.task}
    if sum(args.task.values()) != 8:
        raise ValueError(
            "Please make sure that the summation of the hours is equal to 8. "
            + f"(Given: {sum(args.task.values())} hours)"
        )
    return args


def run():
    """Entry point"""
    # pylint: disable=too-many-statements
    args = parse_args()
    notification_text = None

    config = Config(verbose=args.verbose)

    try:
        clockify = Clockify(config.CLOCKIFY_API_KEY, locale=config.LOCALE)

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
        if not assert_start_date(start_date):
            logger.critical("Start date failed sanity check. Aborting program")
            sys.exit(1)
        working_dates, holidays = get_working_dates(
            start=start_date, count=args.count, cal=cal
        )

        logger.info(
            "Try to submitting %d report(s)... (working days: %s / holidays : %s)",
            args.count,
            working_dates,
            holidays,
        )

        for date in working_dates:
            clockify.submit_clockify(date, args.task, dry_run=args.dry_run)

        for date in holidays:
            clockify.submit_clockify(date, {"holiday": 8}, dry_run=args.dry_run)

        # Notification (OSX only)
        if args.notification and sys.platform.lower() == "darwin":
            if len(working_dates) == 1:
                notification_text = (
                    f"Timesheet for {args.start.lower()} is successfully submitted."
                )
            else:
                date_0 = working_dates[0]
                date_f = working_dates[-1]
                notification_text = (
                    f"Timesheets from {date_0} to {date_f} are successfully submitted."
                )
            if args.dry_run:
                notification_text = f"[DRY_RUN] {notification_text}"
            os.system(
                f"""osascript -e 'display notification "{notification_text}" with title "TP Timesheet"'"""
            )
    except Exception:  # pylint: disable=broad-except
        notification_text = "⚠️ TP Timesheet was not submitted successfully."
        logger.critical(notification_text, exc_info=True)
        os.system(
            f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                    default button "OK" with icon 2'"""
        )


if __name__ == "__main__":
    run()
