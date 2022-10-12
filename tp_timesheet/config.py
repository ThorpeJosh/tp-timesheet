"""Module to store, create or read from a configuration file and parse the values and variables to
globals for other modules to access.
"""
import os
import re
import configparser
from pathlib import Path


class Config:
    """Config class, manages the initialization of all the necesarry globals."""

    # pylint:disable = anomalous-backslash-in-string

    @classmethod
    def __init__(cls, debug=False):
        """This is the entry point for the class and running this will setup the tp-timesheet
        config and make all the necesarry globals available
        """
        cls.VERBOSE = verbose
        cls.CONFIG_DIR = Path.home().joinpath(".config", "tp-timesheet")
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cls.CONFIG_PATH = cls.CONFIG_DIR.joinpath("tp.conf")

        cls.DEFAULT = {"check_max_days": "True", "max_submit_within_days": "7"}

        # Read from config file
        config = cls._read_write_config()

        # Load global configurations
        cls.EMAIL = config.get("configuration", "tp_email")
        cls.URL = config.get("configuration", "tp_url")
        cls.MAX_DAYS = config.get("configuration", "max_submit_within_days")
        cls.CHECK_MAX_DAYS = config.get("configuration", "check_max_days")

    @staticmethod
    def is_valid_email(email):
        """Check email is valid"""
        return re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", email)

    @staticmethod
    def is_valid_url(url):
        """Check url is valid"""
        regex = re.compile(
            r"^https://forms\."  # knowns start to url
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?)"  # domain
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(regex.search(url))

    @classmethod
    def _read_write_config(cls):
        """Function to read the config file or create one if it doesn't exist"""
        config = configparser.ConfigParser(allow_no_value=True)
        # Write config template to file if it doesn't already exist
        if not os.path.exists(cls.CONFIG_PATH):
            print("No config file was found, creating one at:", cls.CONFIG_PATH)
            # Gather input from user to populate the config
            email = input("Enter TP email:")
            while not cls.is_valid_email(email):
                email = input("Invalid email, please try again:")
            url = input("Enter timesheet url:")
            while not cls.is_valid_url(url):
                url = input("Invalid url, please try again:")
            config["configuration"] = {
                "tp_email": email,
                "tp_url": url,
                "check_max_days": "True",
                "max_submit_within_days": 7,
            }

            with open(cls.CONFIG_PATH, "w", encoding="utf8") as config_file:
                config.write(config_file)

        # Read the config file
        if cls.VERBOSE:
            print(f"Reading config file at: {cls.CONFIG_PATH}")
        input_config = configparser.ConfigParser()
        input_config.read(cls.CONFIG_PATH)

        # Version compatibility (#20)
        for config_key in ["check_max_days", "max_submit_within_days"]:
            if not input_config.has_option("configuration", config_key):
                input_config.set("configuration", config_key, cls.DEFAULT[config_key])

        with open(cls.CONFIG_PATH, "w", encoding="utf8") as config_file:
            input_config.write(config_file)

        return input_config
