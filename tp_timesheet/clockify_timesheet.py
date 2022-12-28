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

    task_project_dict = {
        "live": ("Live hours", "Jupiter Staffing APAC"),
        "training": ("Training", "Jupiter Staffing APAC"),
        "OOO": ("Out Of Office", "Jupiter Staffing APAC"),
        "holiday": ("Holiday", "Jupiter Staffing APAC"),
    }
    project_id_cache = {}
    task_id_cache = {}
    locale_id_cache = {}

    api_base_endpoint = "https://api.clockify.me/api/v1"

    def __init__(self, api_key, locale):
        self.api_key = api_key

        (
            self.workspace_id,
            self.user_id,
            self.timezone,
            self.start_time,
        ) = self._get_workspace_user_id()
        self.locale_id = self._get_locale_id(locale)

    def submit_clockify(self, date, task_and_hours, dry_run=False):
        """Submit entry to clockify"""

        if not dry_run:
            # delete time entry if exist
            self.delete_time_entry(date)

        # post entry
        start_time = self.start_time
        for (task, hour) in task_and_hours.items():
            self._post_time_entry(date, task, start_time, hour, dry_run)
            start_time = datetime.time(start_time.hour + hour, 0)

    def _post_time_entry(self, date, task, start_time, hour, dry_run):
        """Post a time entry to clockify"""

        # Timestamps via API need to be UTC
        # Create a timezone aware datetime object
        tz_file = dateutil.tz.gettz(self.timezone)
        start_dt = datetime.datetime.combine(date, start_time, tzinfo=tz_file)
        end_dt = start_dt + datetime.timedelta(hours=hour)
        # Generate ISO (POSIX datetime) strings in UTC format
        start_timestamp = start_dt.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        end_timestamp = end_dt.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        project_id = self.get_project_id(task)
        task_id = self.get_task_id(project_id, task)
        time_entry_json = {
            "start": start_timestamp,
            "end": end_timestamp,
            "billable": True,
            "projectId": project_id,
            "taskId": task_id,
            "tagIds": [self.locale_id],
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

    def get_time_entry_id(self, date):
        """Get a time entry from clockify on a certain date"""

        # Timestamps via API need to be UTC
        # Create a timezone aware datetime object
        tz_file = dateutil.tz.gettz(self.timezone)
        start_dt = datetime.datetime.combine(
            date, datetime.time(0, 0, 0), tzinfo=tz_file
        )
        end_dt = datetime.datetime.combine(
            date, datetime.time(23, 59, 59), tzinfo=tz_file
        )
        # Generate ISO (POSIX datetime) strings in UTC format
        start_timestamp = start_dt.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        end_timestamp = end_dt.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        params = {"start": start_timestamp, "end": end_timestamp}

        response = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/user/{self.user_id}/time-entries",
            headers={"X-Api-Key": self.api_key},
            params=params,
            timeout=2,
        )
        response.raise_for_status()
        response_list = json.loads(response.text)

        # Extract time entries
        time_entry_ids = []
        if response_list:
            for entry in response_list:
                time_entry_ids.append(entry["id"])
        return time_entry_ids

    def delete_time_entry(self, date):
        """Delete a time entry from clockify"""
        time_entry_ids = self.get_time_entry_id(date)
        for entry in time_entry_ids:
            response = requests.delete(
                f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/time-entries/{entry}",
                headers={"X-Api-Key": self.api_key},
                timeout=2,
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

    def get_project_id(self, task_short):
        """Send request to get project id"""
        _, project = self.task_project_dict[task_short]

        if project in self.project_id_cache:
            return self.project_id_cache[project]

        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/projects",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        request_list = json.loads(get_request.text)

        for dic in request_list:
            if dic["name"] == project:
                self.project_id_cache[project] = dic["id"]
                return dic["id"]
        raise ValueError(
            f'Could not find project named "{project}", check your project name'
        )

    def get_task_id(self, project_id, task_short):
        """Send request to get task id"""
        task_full, _ = self.task_project_dict[task_short]

        if task_full in self.task_id_cache:
            return self.task_id_cache[task_full]

        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/projects/{project_id}/tasks",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        request_list = json.loads(get_request.text)

        for dic in request_list:
            if dic["name"] == task_full:
                self.task_id_cache[task_full] = dic["id"]
                return dic["id"]
        raise ValueError(
            f'Could not find task named "{task_short}", check your task name'
        )

    def _get_locale_id(self, locale):
        if locale in self.locale_id_cache:
            return self.locale_id_cache[locale]

        get_request = requests.get(
            f"{self.api_base_endpoint}/workspaces/{self.workspace_id}/tags",
            headers={"X-Api-Key": self.api_key},
            timeout=2,
        )
        get_request.raise_for_status()
        request_list = json.loads(get_request.text)
        for dic in request_list:
            if dic["name"] == locale:
                self.locale_id_cache[locale] = dic["id"]
                return dic["id"]
        raise ValueError(
            f'Could not find locale named "{locale}", check your locale tag'
        )
