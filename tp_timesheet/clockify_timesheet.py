"""Module to submit clockify timesheet, retrieve workspace ID, project ID and task ID
"""
import json
import logging
import requests

logger = logging.getLogger(__name__)


class Clockify:
    """Clockify class, contains all methods required to set up and submit entry to clockify"""

    api_base_endpoint = "https://api.clockify.me/api/v1"

    def __init__(self, api_key):
        self.api_key = api_key

        self.workspace_id = None
        self.project_id = None
        self.task_id = None

    def submit_clockify(self, date, working_hours, dry_run=False):
        """Submit entry to clockify"""
        # Timestamps via API need to be UTC
        start_timestamp = f"{date.isoformat()}T01:00:00.00Z"
        end_timestamp = f"{date.isoformat()}T0{1+working_hours}:00:00.00Z"

        time_entry_json = {
            "start": start_timestamp,
            "end": end_timestamp,
            "billable": True,
            "projectId": self.project_id,
            "taskId": self.task_id,
        }

        # Use fake api_key if in dry_mode
        api_key = "1234" if dry_run else self.api_key

        response = requests.post(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/time-entries",
            headers={"X-Api-Key": api_key},
            json=time_entry_json,
            timeout=2,
        )
        response.raise_for_status()
        logger.debug("POST:  %s\nResponse: %s", time_entry_json, response.text)

    def get_workspace_id(self):
        """Send request to get workspace id"""
        get_request = requests.get(
            "https://api.clockify.me/api/v1/user",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        request_dict = json.loads(get_request.text)
        self.workspace_id = request_dict["activeWorkspace"]

    def get_project_id(self):
        """Send request to get project id"""
        return

    def get_task_id(self):
        """Send request to get task id"""
        return
