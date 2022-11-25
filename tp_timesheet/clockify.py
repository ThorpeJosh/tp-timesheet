import requests

class Clockify:
    """Clockify class, contains all methods required to set up and submit entry to clockify
    """

    api_base_endpoint = "https://api.clockify.me/api/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def submit_clockify(self, date, working_hours, verbose = False, dry_run = False):
        # TODO: write python script to submit clockify entry

