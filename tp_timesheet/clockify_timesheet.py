"""Module to submit clockify timesheet, retrieve workspace ID, project ID and task ID
"""
import json
import logging
import datetime
import dateutil
import requests

logger = logging.getLogger(__name__)


class Clockify:
    """Clockify class, contains all methods required to set up and submit entry to clockify"""

    # pylint: disable=too-few-public-methods

    api_base_endpoint = "https://api.clockify.me/api/v1"

    def __init__(self, api_key, project, task):
        self.api_key = api_key

        (
            self.workspace_id,
            self.user_id,
            self.timezone,
            self.start_time,
        ) = self._get_workspace_user_id()
        self.project_id = self._get_project_id(project)
        self.task_id = self._get_task_id(task)

    def submit_clockify(self, date, working_hours, dry_run=False):
        """Submit entry to clockify"""
        # Retrieve project and task ids based on what the user specifies
        # Timestamps via API need to be UTC
        # Create a timezone aware datetime object
        tz_file = dateutil.tz.gettz(self.timezone)
        start_dt = datetime.datetime.combine(date, self.start_time, tzinfo=tz_file)
        end_dt = start_dt + datetime.timedelta(hours=working_hours)
        # Generate ISO (POSIX datetime) strings in UTC format
        start_timestamp = start_dt.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        end_timestamp = end_dt.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        time_entry_json = {
            "start": start_timestamp,
            "end": end_timestamp,
            "billable": True,
            "projectId": self.project_id,
            "taskId": self.task_id,
        }

        if dry_run:
            logger.debug("This is a DRY-RUN, api POST is not being sent")
            logger.debug("POST:  %s\n", time_entry_json)
        else:
            response = requests.post(
                f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/time-entries",
                headers={"X-Api-Key": self.api_key},
                json=time_entry_json,
                timeout=2,
            )
            logger.debug(
                "POST:  %s\nResponse: %s",
                time_entry_json,
                response.text,
            )
            response.raise_for_status()

    def _get_workspace_user_id(self):
        """Send request to get workspace id

        Args:
            self: self

        Returns:
            workspace_id (str): workspace identifier
            user_id (str): user identifier
            timezone (str): timezone in Region/City format eg) 'Asia/Singapore'
            start_time (datetime.time): time object eg) datetime.time(8, 30)
        """
        get_request = requests.get(
            f"{self.api_base_endpoint}/user",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        request_dict = json.loads(get_request.text)
        workspace_id = request_dict["activeWorkspace"]
        user_id = request_dict["id"]
        timezone = request_dict["settings"]["timeZone"]
        start_time_str = request_dict["settings"]["myStartOfDay"]
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
        return workspace_id, user_id, timezone, start_time

    def _get_project_id(self, project):
        """Send request to get project id"""
        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/projects",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        request_list = json.loads(get_request.text)
        for dic in request_list:
            if dic["name"] == project:
                return dic["id"]
        raise ValueError(
            f'Could not find project named "{project}", check your API key'
        )

    def _get_task_id(self, task):
        """Send request to get task id"""
        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/projects/{self.project_id}/tasks",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        request_list = json.loads(get_request.text)
        for dic in request_list:
            if dic["name"] == task:
                return dic["id"]
        raise ValueError(f'Could not find task named "{task}", check your API key')

    # def _get_tag_id(self):
