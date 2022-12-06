"""Module to store, create or read from a configuration file and parse the values and variables to
globals for other modules to access.
"""
import logging
import logging.handlers
import os
import re
import configparser
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """Config class, manages the initialization of all the necessary globals."""

    # pylint:disable = anomalous-backslash-in-string
    ROOT_LOGGER = None
    CONFIG_DIR = Path.home().joinpath(".config", "tp-timesheet")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR = Path.joinpath(CONFIG_DIR, "logs")
    LOG_DIR.mkdir(exist_ok=True)
    LOG_PATH = LOG_DIR.joinpath("tp.logs")

    # config parameters (need to be accessible to tests without invoking __init__)
    sanity_check_bool_dict = {"sanity_check_start_date": "True"}
    sanity_check_range_dict = {"sanity_check_range": "7"}
    clockify_api_key = {
        "clockify_api_key": "AbCD1234AbCD1234AbCD1234AbCD1234AbCD1234AbCD1234"
    }
    locale_list = ["en_AU", "en_SG", "ko_KR", "ms_MY", "th_TH"]
    locale_tag = {"locale_tag": "xx_XX"}
    DEFAULT_CONF = {
        **sanity_check_bool_dict,
        **sanity_check_range_dict,
        **clockify_api_key,
        **locale_tag,
    }

    @classmethod
    def __init__(cls, verbose=False, config_filename="tp.conf"):
        """This is the entry point for the class and running this will setup the tp-timesheet
        config and make all the necessary globals available
        """
        cls.VERBOSE = verbose
        cls.CONFIG_DIR = Config.CONFIG_DIR
        cls.CONFIG_PATH = cls.CONFIG_DIR.joinpath(config_filename)

        # Initialize root logger
        cls.init_logger()

        # Read from config file
        config = cls._read_write_config()

        # Load global configurations
        cls.EMAIL = config.get("configuration", "tp_email")
        cls.URL = config.get("configuration", "tp_url")
        cls.LOCALE = config.get("configuration", "locale_tag")
        cls.SANITY_CHECK_START_DATE = config.get(
            "configuration", next(iter(cls.sanity_check_bool_dict))
        )
        cls.SANITY_CHECK_RANGE = config.get(
            "configuration", next(iter(cls.sanity_check_range_dict))
        )
        cls.CLOCKIFY_API_KEY = config.get(
            "configuration", next(iter(cls.clockify_api_key))
        )

    @classmethod
    def init_logger(cls):
        """Initialze root logger."""

        # create root logger
        cls.ROOT_LOGGER.setLevel(logging.DEBUG)

        # create formatter
        log_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # log to stdout
        level = logging.DEBUG if cls.VERBOSE else logging.INFO
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(log_format)
        cls.ROOT_LOGGER.addHandler(stream_handler)

        # log to file, rotate every 4 weeks, save up to 8 weeks
        file_handler = logging.handlers.TimedRotatingFileHandler(
            Config.LOG_PATH, when="W6", interval=4, backupCount=8
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        cls.ROOT_LOGGER.addHandler(file_handler)

    @staticmethod
    def is_valid_email(email):
        """Check email is valid"""
        return re.search(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", email)

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

    @staticmethod
    def is_valid_key(api_key):
        """Check api key is valid"""
        regex_api = bool(re.match("^[A-Za-z0-9]*$", api_key))
        len_api = len(api_key) > 40
        return regex_api & len_api

    @classmethod
    def is_valid_locale(cls, locale):
        """Check locale is valid"""
        valid = locale in cls.locale_list
        return valid

    @classmethod
    def _read_write_config(cls):
        """Function to read the config file or create one if it doesn't exist"""
        config = configparser.ConfigParser(allow_no_value=True)
        # Write config template to file if it doesn't already exist
        if not os.path.exists(cls.CONFIG_PATH):
            logger.info(
                "No config file was found, creating one at: %s", cls.CONFIG_PATH
            )
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
            config["configuration"].update(cls.DEFAULT_CONF)

            with open(cls.CONFIG_PATH, "w", encoding="utf8") as config_file:
                config.write(config_file)

        # Read the config file
        if cls.VERBOSE:
            logger.debug("Reading config file at: %s", cls.CONFIG_PATH)
        input_config = configparser.ConfigParser()
        input_config.read(cls.CONFIG_PATH)

        # Version compatibility (#20)
        # Creates all config keys that don't exists yet and sets to default values
        for config_key, config_value in cls.DEFAULT_CONF.items():
            if not input_config.has_option("configuration", config_key):
                input_config.set("configuration", config_key, config_value)

        # Version compatability (#65)
        # Will check to ensure API key has been changed from the default value
        if (
            input_config.get("configuration", next(iter(cls.clockify_api_key)))
            == cls.clockify_api_key[next(iter(cls.clockify_api_key))]
        ):
            clockify_api = input("Enter clockify API key:")
            while not cls.is_valid_key(clockify_api):
                clockify_api = input("Invalid api key, please try again:")
            input_config.set(
                "configuration", next(iter(cls.clockify_api_key)), clockify_api
            )
        if (
            input_config.get("configuration", next(iter(cls.locale_tag)))
            == cls.locale_tag[next(iter(cls.locale_tag))]
        ):
            poss_locales = cls.locale_list
            locale_tag = input(f"Enter locale tag ({poss_locales}):")
            while not cls.is_valid_locale(locale_tag):
                locale_tag = input(f"Please choose from {poss_locales}, try again:")
            input_config.set("configuration", next(iter(cls.locale_tag)), locale_tag)

        with open(cls.CONFIG_PATH, "w", encoding="utf8") as config_file:
            input_config.write(config_file)

        return input_config
