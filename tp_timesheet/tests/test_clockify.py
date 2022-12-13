"""Unit tests for the retrieving of ids"""
import random
import datetime
import json
import requests
from tp_timesheet.clockify_timesheet import Clockify
from tp_timesheet.config import Config

# Import config fixture from adjacent test
# pylint: disable=(unused-import)
from .test_config import fixture_create_tmp_clockify_api_config

WORKSPACE_ID = "5fa423e902f38d2ce68f3169"
PROJECT_ID = "6377ce7d0c7a4c4566b89d41"
TASK_IDS = [
    "6377ce9c0c7a4c4566b89ef7",  # Live hours
    "6377cea7d3400c1c832e48cb",  # Training
    "63ab0fa9563a041b5b01148a",  # Out Of Office
    "63ab0fa627acb5055e805c0b",  # Holiday
]


def test_ids(clockify_config):
    """
    Test for checking validity of workspace, project and task ids obtained from request
    """
    config = Config(config_filename=clockify_config)
    clockify_val = Clockify(api_key=config.CLOCKIFY_API_KEY, locale=config.LOCALE)
    assert (
        clockify_val.workspace_id == WORKSPACE_ID
    ), f"Workspace ID Error, expected: {WORKSPACE_ID}, result:{clockify_val.workspace_id}"

    for task_idx, task_short in enumerate(["live", "training", "OOO", "holiday"]):
        project_id = clockify_val.get_project_id(task_short)
        assert (
            project_id == PROJECT_ID
        ), f"Project ID Error, expected: {PROJECT_ID}, result:{project_id}"
        assert (
            task_id == TASK_IDS[task_idx]
        ), f"Project ID Error, expected: {TASK_IDS[task_idx]}, result:{task_id}"


def test_remove_existing_entries(clockify_config):
    """Test removal of clockify time entries.

    Test coverage:
      *  Tests that the existing time entries can be retreived for a particular day,
      *  Tests that the entries for a particular day can all be cleared
      *  Tests that max of one entry exists per day
    """

    def assert_number_of_entries(test_date, number_of_entries):
        actual_number_of_entries = len(clockify.get_time_entry_id(test_date))
        assert actual_number_of_entries == number_of_entries, (
            f"Incorrect number of entries, expected: {number_of_entries},"
            f"returned: {actual_number_of_entries}\n"
            f"TESTING DATE: {test_date}"
        )

    # Instantiate a Clockify object
    config = Config(config_filename=clockify_config)
    clockify = Clockify(api_key=config.CLOCKIFY_API_KEY, locale=config.LOCALE)

    # Use following date as test date. Random future date in January
    test_date = datetime.date(
        2025 + random.randrange(0, 10, 1), 1, 1 + random.randrange(0, 30, 1)
    )

    # Remove all entries incase any are left over from previous tests
    clockify.delete_time_entry(test_date)

    # Check no entry exists
    assert_number_of_entries(test_date, 0)

    # Add a clockify entry with 1 hour
    clockify.submit_clockify(test_date, {"live": 4})

    # Check only one entry exists
    assert_number_of_entries(test_date, 1)

    # Remove all entries
    clockify.delete_time_entry(test_date)

    # Resubmit clockify entry with 4 hours
    clockify.submit_clockify(test_date, {"OOO": 4})

    # Check only one entry exists
    assert_number_of_entries(test_date, 1)

    # Remove all entries
    clockify.delete_time_entry(test_date)

    # Check no entry exists
    assert_number_of_entries(test_date, 0)


def test_time_entry_tags(clockify_config):
    """Test that time entries include a tag"""

    # Instantiate a Clockify object
    config = Config(config_filename=clockify_config)
    clockify = Clockify(api_key=config.CLOCKIFY_API_KEY, locale=config.LOCALE)

    # Use following date as test date. Random future date in January
    test_date = datetime.date(
        2025 + random.randrange(0, 10, 1), 1, 1 + random.randrange(0, 30, 1)
    )

    # Remove all entries incase any are left over from previous tests
    clockify.delete_time_entry(test_date)

    # Add a clockify entry
    clockify.submit_clockify(test_date, {"live": 8})

    # Check entry contains a tag with the intended locale
    task_id = clockify.get_time_entry_id(test_date)
    assert len(task_id) == 1
    task_id = task_id[0]
    response = requests.get(
        f"{clockify.api_base_endpoint}/workspaces/{clockify.workspace_id}/time-entries/{task_id}",
        headers={"X-Api-Key": clockify.api_key},
        timeout=2,
    )
    response.raise_for_status()
    response_dict = json.loads(response.text)
    # Check tag ids match
    assert response_dict["tagIds"] == [clockify.locale_id]
    # Check tag name is as expected
    response = requests.get(
        f"{clockify.api_base_endpoint}/workspaces/{clockify.workspace_id}/tags/{clockify.locale_id}",
        headers={"X-Api-Key": clockify.api_key},
        timeout=2,
    )
    response.raise_for_status()
    response_dict = json.loads(response.text)
    assert response_dict["name"] == config.LOCALE

    # Remove all entries
    clockify.delete_time_entry(test_date)
