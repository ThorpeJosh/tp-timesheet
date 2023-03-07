""" TP-Timesheet Module"""
import logging
from tp_timesheet.config import Config

__version__ = "2.1.0"

logger = logging.getLogger(__name__)
Config.ROOT_LOGGER = logger
