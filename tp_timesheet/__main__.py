""" Entry point for cli """
import os
import argparse
from tp_timesheet.docker_handler import DockerHandler
from tp_timesheet.submit_form import submit_timesheet
from tp_timesheet.dates import date_fn
from datetime import datetime


def parse_args():
    """Parse arguments from the command line"""
    parser = argparse.ArgumentParser(description='TP Automated Timesheet Submission - CLI Tool')
    parser.add_argument('-s', '--start', type=str, required=True,
                        help="First date to submit a timesheet for, dd/mm/yy or 'today'")
    parser.add_argument('-c', '--count', type=int, required=False, default=1,
                        help="Number of weekdays to submit a timesheet for, use '5' on a monday to submit for the entire week")
    parser.add_argument('-d', '--debug', action='store_true',
                      help='Debug mode, saves screenshots of the timesheet submission page to your desktop')
    return parser.parse_args()

def run():
    """Entry point"""
    URL = os.getenv('TP_URL')
    EMAIL = os.getenv('TP_EMAIL')
    if URL is None: 
        raise ValueError("URL is not set, please run `export TP_URL='<URL OF TIMESHEET>'")
    if EMAIL is None:
        raise ValueError("EMAIL is not set, please run `export TP_EMAIL='<TP EMAIL ADDR>'")

    args = parse_args()
    if args.start.lower() == "today":
        start_date = datetime.today()
    else:
        start_date = datetime.strptime(args.start, "%d/%m/%Y")
    dates = date_fn(start = start_date, count = args.count)
    print("Date(s) to be submitted (YYYY-mm-dd):", [str(d) for d in dates])
    



    docker_handler = DockerHandler()
    try:
        if args.debug:
            print('Pulling latest image')
        docker_handler.pull_image()
        if args.debug:
            print('Launching docker container for selenium backend')
        docker_handler.run_container()

        # TODO: Run the timesheet submissions for each date
        # submit_timesheet(URL, EMAIL, date, args.debug)

    finally:
        if args.debug:
            print('Cleaning up docker container')
        if docker_handler.container is not None:
            docker_handler.rm_container()

if __name__ == '__main__':
    run()

