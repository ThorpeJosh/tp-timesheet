""" Entry point for cli """
import os
import argparse
from tp_timesheet.docker_handler import DockerHandler
from tp_timesheet.submit_form import submit_timesheet
from tp_timesheet.dates import date_fn
from tp_timesheet.schedule import ScheduleForm
from tp_timesheet.config import Config
from datetime import datetime
from workalendar.asia import Singapore


def parse_args():
    """Parse arguments from the command line"""
    parser = argparse.ArgumentParser(description='TP Automated Timesheet Submission - CLI Tool')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--start', type=str,
                        help="Normal mode: Indicating first date to submit a timesheet. Accepted arguments = ['dd/mm/yy' ,today]")
    group.add_argument('-a', '--automate', type=str,
                        help="Automate mode: Schedules the form submission to run automatically. Accepted arguments = [weekdays]")
    parser.add_argument('-c', '--count', type=int, required=False, default=1,
                        help="Number of weekdays to submit a timesheet for, use '5' on a monday to submit for the entire week")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose mode, prints logs and saves screenshots of the timesheet submission page to your desktop')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Dry run mode, runs through as per normal but will not click submit')
    return parser.parse_args()

def run():
    """Entry point"""
    args = parse_args()
    config = Config()
    # Automate Mode
    if args.automate is not None:
        valid_options = ['weekdays']
        if args.automate not in valid_options:
            print(f"'{args.automate}' is not a valid option for --automate mode")
            return
        scheduler = ScheduleForm()
        scheduler.schedule()
        return

    # Normal Mode
    cal = Singapore()
    if args.start.lower() == "today":
        start_date = datetime.today()
    else:
        start_date = datetime.strptime(args.start, "%d/%m/%Y")
    dates = date_fn(start = start_date, count = args.count, cal = cal)
    print(f"Date(s) (YYYY-mm-dd) to be submitted for {config.EMAIL}:", [str(date) for date in dates])

    docker_handler = DockerHandler()
    try:
        if args.verbose:
            print('Pulling latest image')
        docker_handler.pull_image()
        if args.verbose:
            print('Launching docker container for selenium backend')
        docker_handler.run_container()

        for date in dates:
            submit_timesheet(config.URL, config.EMAIL, date, verbose=args.verbose, dry_run=args.dry_run)

    finally:
        if args.verbose:
            print('Cleaning up docker container')
        if docker_handler.container is not None:
            docker_handler.rm_container()

if __name__ == '__main__':
    run()

