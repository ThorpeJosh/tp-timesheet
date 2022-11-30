"""Unit tests for the config module"""
import builtins
import os
import sys
import configparser
import pytest
import mock
from tp_timesheet.config import Config

tests_path = os.path.dirname(os.path.abspath(__file__))
src_path = tests_path + "/../"
sys.path.insert(0, src_path)


@pytest.fixture(name="mock_config")
def fixture_create_tmp_mock_config():
    """
    Creates a tmp config file with arbitrary values prior to running a test that uses this fixture.
    It then cleans up the tmp file after the test has run
    """
    # Fake config loaded by pytest
    test_config_path = Config.CONFIG_DIR.joinpath("tmp_pytest.conf")
    config_str = """
[configuration]
tp_email = fake@email.com
tp_url = https://example.com/path
clockify_api_key = some_random_api
    """
    with open(test_config_path, "w", encoding="utf8") as conf_file:
        conf_file.write(config_str)
    yield test_config_path
    os.remove(test_config_path)


@pytest.fixture(name="clockify_config")
def fixture_create_tmp_clockify_api_config():
    """
    Creates a tmp config file containing the clockify api prior to running a test that uses this fixture.
    It then cleans up the tmp file after the test has run
    """
    # Fake config loaded by pytest
    test_config_path = Config.CONFIG_DIR.joinpath("tmp_pytest.conf")
    if os.getenv("CLOCKIFY_CRED"):
        api_key = os.getenv("CLOCKIFY_CRED")
    else:
        config = Config()
        api_key = config.CLOCKIFY_API_KEY
    config_str = f"""
[configuration]
tp_email = fake@email.com
tp_url = https://example.com/path
clockify_api_key = {api_key}
    """
    with open(test_config_path, "w", encoding="utf8") as conf_file:
        conf_file.write(config_str)
    print(config_str)
    yield test_config_path
    os.remove(test_config_path)


@pytest.fixture(name="tmp_v3_config")
def fixture_create_v3_0_0_config():
    """
    Creates a tmp config file with parameters from <=v0.3.0.
    It then cleans up the tmp file after the test has run
    """
    # Fake config loaded by pytest
    test_config_path = Config.CONFIG_DIR.joinpath("tmp_pytest.conf")
    config_str = """
[configuration]
tp_email = fake@email.com
tp_url = https://example.com/path
    """
    with open(test_config_path, "w", encoding="utf8") as conf_file:
        conf_file.write(config_str)
    yield test_config_path
    os.remove(test_config_path)


def test_config_upgrade_process(tmp_v3_config):
    """
    test the config from <=0.3.0 (email and url only),
    upgrades succesfully to include new parameters
    """
    new_parameters = Config.DEFAULT_CONF

    def read_config_as_text(path):
        with open(path, "r", encoding="utf8") as config_f:
            return config_f.readlines()

    def read_config_as_dict(path):
        input_config = configparser.ConfigParser()
        input_config.read(path)
        return input_config

    # Check config file exists already (created by fixture)
    assert os.path.exists(tmp_v3_config)

    # Assert no config parameters exist in config prior to upgrade
    config_text = read_config_as_text(tmp_v3_config)
    for line in config_text:
        for parameter in new_parameters:
            assert parameter not in line

    # Test config file reads correctly and only <=0.3.0 parameters exist
    config_dict = read_config_as_dict(tmp_v3_config)
    assert config_dict.sections() == ["configuration"]
    assert list(config_dict["configuration"]) == ["tp_email", "tp_url"]

    # Initialize config which performs the upgrade
    with mock.patch.object(
        builtins, "input", lambda _: new_parameters["clockify_api_key"]
    ):
        Config(config_filename=tmp_v3_config)

    # Test config file reads correctly and contains all the new parameters
    config_dict = read_config_as_dict(tmp_v3_config)
    assert config_dict.sections() == ["configuration"]
    assert sorted(list(config_dict["configuration"])) == sorted(
        ["tp_email", "tp_url"] + list(new_parameters.keys())
    )
    for key, item in new_parameters.items():
        assert config_dict.get("configuration", key) == item
