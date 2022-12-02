"""Unit tests for the retrieving of ids"""
import random
import datetime
from tp_timesheet.clockify_timesheet import Clockify
from tp_timesheet.config import Config

# Import config fixture from adjacent test
# pylint: disable=(unused-import)
from .test_config import fixture_create_tmp_clockify_api_config

WORKSPACE_ID = "5fa423e902f38d2ce68f3169"
PROJECT_IDS = [
    "6377ce7d0c7a4c4566b89d41",  # Jupiter Staffing APAC
    "63120a634420051596d195ee",  # Jupiter Non-Billable
]
TASK_IDS = [
    "6377ce9c0c7a4c4566b89ef7",  # Live hours
    "6377cea7d3400c1c832e48cb",  # Training
    "63120a6db1479f58e2d04b77",  # Out Of Office
    "6368f01245b6796dca64e8f5",  # Holiday
]


def test_ids(clockify_config):
    """
    Test for checking validity of workspace, project and task ids obtained from request
    """
    config = Config(config_filename=clockify_config)
    tasks = ["live", "training", "OOO", "holiday"]
    for selected_t in tasks:
        clockify_val = Clockify(
            api_key=config.CLOCKIFY_API_KEY, task=selected_t, locale="en_SG"
        )
        assert (
            clockify_val.workspace_id == WORKSPACE_ID
        ), f"Workspace ID Error, expected: {WORKSPACE_ID}, result:{clockify_val.workspace_id}"
        assert (
            clockify_val.project_id in PROJECT_IDS
        ), f"Project ID Error, expected value from: {PROJECT_IDS}, result:{clockify_val.project_id}"
        assert (
            clockify_val.task_id in TASK_IDS
        ), f"Task ID Error, expected value from: {TASK_IDS}, result:{clockify_val.task_id}"


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
    clockify = Clockify(api_key=config.CLOCKIFY_API_KEY, task="training")

    # Use following date as test date. Random future date in January
    test_date = datetime.date(
        2022 + random.randrange(1, 10, 1), 1, 1 + random.randrange(0, 30, 1)
    )

    # Remove all entries incase any are left over from previous tests
    clockify.delete_time_entry(test_date)

    # Check no entry exists
    assert_number_of_entries(test_date, 0)

    # Add a clockify entry with 1 hour
    clockify.submit_clockify(test_date, 1)

    # Check only one entry exists
    assert_number_of_entries(test_date, 1)

    # Resubmit clockify entry with 4 hours
    clockify.submit_clockify(test_date, 4)

    # Check only one entry exists still
    assert_number_of_entries(test_date, 1)

    # Remove all entries
    clockify.delete_time_entry(test_date)

    # Check no entry exists
    assert_number_of_entries(test_date, 0)
