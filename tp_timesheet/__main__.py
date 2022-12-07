""" Entry point for cli """
import logging
import os
import sys
import argparse
import warnings
import selenium
import docker
from workalendar.asia import Singapore
from tp_timesheet import __version__
from tp_timesheet.docker_handler import DockerHandler, DockerHandlerException
from tp_timesheet.submit_form import submit_timesheet
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
        "--hours",
        type=int,
        default=8,
        help="Number of hours to submit. Default=8",
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
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-t",
        "--task",
        type=str,
        default="live",
        choices=["holiday", "live", "OOO", "training"],
        help="The type of task for the clockify submission. Specify task name "
        + "if it is anything other than 'live'. Put the task name (e.g., training, OOO, holiday)",
    )
    return parser.parse_args()


def run():
    """Entry point"""
    # pylint: disable=too-many-statements
    args = parse_args()
    notification_text = None
    docker_handler = None
    notification_flag = False

    config = Config(verbose=args.verbose)

    try:
        DockerHandler.install_and_launch_docker()
        clockify = Clockify(
            config.CLOCKIFY_API_KEY, task=args.task, locale=config.LOCALE
        )

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
        dates = get_working_dates(
            start=start_date, count=args.count, cal=cal, working_hours=args.hours
        )

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

            clockify.submit_clockify(date, working_hours=hours, dry_run=args.dry_run)

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
    except docker.errors.DockerException:
        notification_text = (
            "⚠️ TP-timesheet was not submitted successfully. Check if Docker is running"
        )
        logger.critical(notification_text, exc_info=True)
        os.system(
            f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                    default button "OK" with icon 2'"""
        )
    except selenium.common.exceptions.NoSuchElementException:
        notification_text = "⚠️ TP-timesheet was not submitted successfully. An element on the url \
was not found by Selenium"
        logger.critical(notification_text, exc_info=True)
        os.system(
            f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                    default button "OK" with icon 2'"""
        )
        notification_flag = True
    except DockerHandlerException as error:
        notification_text = f"⚠️ TP-timesheet was not submitted successfully. {error}"
        logger.critical(notification_text, exc_info=True)
        os.system(
            f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                    default button "OK" with icon 2'"""
        )
        notification_flag = True
    except Exception:  # pylint: disable=broad-except
        notification_text = "⚠️ TP Timesheet was not submitted successfully."
        logger.critical(notification_text, exc_info=True)
        os.system(
            f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                    default button "OK" with icon 2'"""
        )
        notification_flag = True
    finally:
        try:
            logger.debug("Cleaning up docker container")
            if docker_handler is not None:
                docker_handler.rm_container()
        except Exception:  # pylint: disable=broad-except
            notification_text = "Ran into an unexpected error while attempting to clean up docker container"
            logger.critical(notification_text, exc_info=True)
            if not notification_flag:
                # Don't show two notifications sequentially
                os.system(
                    f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                        default button "OK" with icon 2'"""
                )


if __name__ == "__main__":
    run()
