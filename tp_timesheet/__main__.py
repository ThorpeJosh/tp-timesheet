""" Entry point for cli """
import os
import argparse

def run():
    """Entry point"""
    URL = os.getenv('TPURL')
    EMAIL = os.getenv('TPEMAIL')
    if URL is None: 
        raise ValueError("URL is not set, please run `export TPURL='<URL OF TIMESHEET>'")
    if EMAIL is None:
        raise ValueError("EMAIL is not set, please run `export TPMAIL='<TP EMAIL ADDR>'")

    args = parse_args()
    print(args)


def parse_args():
    """Parse arguments from the command line"""
    parser = argparse.ArgumentParser(description='TP Automated Timesheet Submission - CLI Tool')
    parser.add_argument('-s', '--start', type=str, required=True,
                        help="First date to submit a timesheet for, dd/mm/yy or 'today'")
    parser.add_argument('-c', '--count', type=int, required=False, default=1,
                        help="Number of weekdays to submit a timesheet for, use '5' on a monday to submit for the entire week")
    parser.add_argument('-d', '--debug', action='store', default=False,
                      help='Debug mode, saves screenshots of the timesheet submission page to your desktop')
    return parser.parse_args()


if __name__ == '__main__':
    run()

