"""Module to submit clockify timesheet, retrieve workspace ID, project ID and task ID
"""

class Clockify:
    """Clockify class, contains all methods required to set up and submit entry to clockify"""

    api_base_endpoint = "https://api.clockify.me/api/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def submit_clockify(
        self, date, working_hours, verbose=False, dry_run=False
    ):  # pylint: disable=unused-argument
        """Submit entry to clockify"""
        # TODO: write python script to submit clockify entry # pylint: disable=fixme
        return

    def get_workspace_id(self):
        """Send request to get workspace id"""
        return

    def get_project_id(self):
        """Send request to get project id"""
        return

    def get_task_id(self):
        """Send request to get task id"""
        return
