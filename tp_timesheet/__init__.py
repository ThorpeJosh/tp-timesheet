""" TP-Timesheet Module"""
import logging
from pathlib import Path

__version__ = "0.2.2"

# create root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create formatter
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# log to stdout
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(log_format)
logger.addHandler(stream_handler)

# log to file
log_dir = Path.home().joinpath(".config", "tp-timesheet.log")
file_handler = logging.FileHandler(log_dir)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)
