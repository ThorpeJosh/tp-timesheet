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

        self.workspace_id, self.user_id = self._get_workspace_user_id()
        self.project_id = self._get_project_id()
        self.task_id = self._get_task_id()

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

        if dry_run:
            logger.debug("This is a DRY-RUN, api POST is not being sent")
        else:
            response = requests.post(
                f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/time-entries",
                headers={"X-Api-Key": self.api_key},
                json=time_entry_json,
                timeout=2,
            )
            response.raise_for_status()
        logger.debug(
            "Dry-run: %s POST:  %s\nResponse: %s",
            dry_run,
            time_entry_json,
            response.text,
        )

    def _get_workspace_user_id(self):
        """Send request to get workspace id"""
        get_request = requests.get(
            self.api_base_endpoint,
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        logger.debug("Response: %s", get_request.text)
        request_dict = json.loads(get_request.text)
        workspace_id = request_dict["activeWorkspace"]
        user_id = request_dict["id"]
        return workspace_id, user_id

    def _get_project_id(self):
        """Send request to get project id"""
        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/projects",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        if get_request.status_code != "200":
            logger.error(
                "Get project ID error, return code %s, check your API key",
                get_request.status_code,
            )
            return None
        request_list = json.loads(get_request.text)
        for dic in request_list:
            if dic["name"] == "Jupiter Staffing APAC":
                return dic["id"]
        logger.error(
            'Could not find project named "Jupiter Staffing APAC", check your API key'
        )
        return None

    def _get_task_id(self):
        """Send request to get task id"""
        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/projects/{self.project_id}/tasks",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        if get_request.status_code != "200":
            logger.error(
                "Get project ID error, return code %s, check your API key",
                get_request.status_code,
            )
            return None
        request_list = json.loads(get_request.text)
        for dic in request_list:
            if dic["name"] == "Live hours":
                return dic["id"]
        logger.error(
                'Could not find task named "Live hours", check your API key'
        )
        return None
