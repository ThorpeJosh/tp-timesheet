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
    def __init__(cls, url=None, email=None, debug=False):
        """This is the entry point for the class and running this will setup the tp-timesheet
        config and make all the necesarry globals available
        """
        cls.URL = url
        cls.EMAIL = email
        cls.DEBUG = debug
        cls.CONFIG_DIR = Path.home().joinpath(".config", "tp-timesheet")
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cls.CONFIG_PATH = cls.CONFIG_DIR.joinpath("tp.conf")

        # Read from config file
        config = cls._read_write_config()

        # Load global configurations
        cls.EMAIL = config.get("configuration", "tp_email")
        cls.URL = config.get("configuration", "tp_url")

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
            }

            with open(cls.CONFIG_PATH, "w", encoding="utf8") as config_file:
                config.write(config_file)

        # Read the config file
        if cls.DEBUG:
            print("Reading config file at: %s", cls.CONFIG_PATH)
        input_config = configparser.ConfigParser()
        input_config.read(cls.CONFIG_PATH)
        return input_config
