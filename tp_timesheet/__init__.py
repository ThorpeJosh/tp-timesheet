""" TP-Timesheet Module"""
import logging
from tp_timesheet.config import Config

__version__ = "0.2.2"

logger = logging.getLogger(__name__)
Config.init_logger(logger)
