""" Automated cron scheduler for daily submissions """
import os
import sysconfig
import sys
import logging
from datetime import datetime
from crontab import CronTab

TP_BIN = "tp-timesheet"
SYS_PATH = os.environ.get("PATH")

logger = logging.getLogger(__name__)


class ScheduleForm:
    """Cron Schedule Handler"""

    def __init__(self):
        self.executable = self.find_executable_location()

    @staticmethod
    def find_executable_location():
        """
        Search and locate the TP_BIN executable that was installed by pip
        Unfortunately pip does not install in a predictable manner or have a mechanism to get the location
        """
        # Check if this is running in a conda env
        sysconfig_scripts_path = sysconfig.get_path("scripts")
        if "conda" in sysconfig_scripts_path:
            bins = os.listdir(sysconfig_scripts_path)
            if TP_BIN in bins:
                return os.path.join(sysconfig_scripts_path, TP_BIN)
            raise ValueError(
                f"It appears you are running in a conda env but the {TP_BIN} binary \
cannot be found in: {sysconfig_scripts_path}"
            )

        # Check prefix path (should work on *NIX, not later MacOS though)
        prefix_bin_path = os.path.join(sys.prefix, "bin")
        if TP_BIN in os.listdir(prefix_bin_path):
            return os.path.join(prefix_bin_path, TP_BIN)

        # Search path relative to this file
        current_file_path = os.path.abspath(__file__)
        python_scripts_path = None
        if "lib" in current_file_path:
            python_scripts_path = os.path.join(
                current_file_path.split("/lib/")[0], "bin"
            )
            if TP_BIN in os.listdir(python_scripts_path):
                return os.path.join(python_scripts_path, TP_BIN)

        raise ValueError(
            f"Could not find the '{TP_BIN}' executable, searched: ",
            [sysconfig_scripts_path, prefix_bin_path, python_scripts_path],
        )

    def schedule(self):
        """Create the crontab schedule"""
        with CronTab(user=True) as cron:
            job = cron.new(
                command=f"PATH='{SYS_PATH}' {self.executable} --start today --count 1 --notification"
            )
            job.minute.parse(30)
            job.hour.parse(9)
            job.dow.parse("MON-FRI")
            assert job.is_valid()
            cron_schedule = job.schedule(date_from=datetime.now())
        logger.info(
            "Job has been scheduled in your crontab, the next scheduled run will be on %s.",
            cron_schedule.get_next(),
        )
        logger.info("Run `crontab -l` to see your scheduled tasks.")
        logger.info("Run `crontab -r` to clear all scheduled tasks.")


if __name__ == "__main__":
    # Executable for debugging purposes
    schedule = ScheduleForm()
    schedule.schedule()
