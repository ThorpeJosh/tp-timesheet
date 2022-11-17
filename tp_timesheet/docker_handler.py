""" Handler for running selenium and chrome backend """
import os
import sys
import platform
import subprocess
import logging
import time
import http
import urllib
import urllib3
import docker
from selenium import webdriver

ARM_IMAGE = "seleniarm/standalone-chromium:105.0"
X86_IMAGE = "selenium/standalone-chrome:105.0"

logger = logging.getLogger(__name__)


class DockerHandlerException(Exception):
    """Exceptions for DockerHandler class"""


class DockerHandler:
    """Docker handler"""

    def __init__(self):
        self.client = docker.from_env()
        self.arch = platform.machine()
        self.image = self.select_image(self.arch)
        self.container = None

    @staticmethod
    def select_image(arch):
        """Select the correct image based on the client architecture"""
        if arch == "arm64":
            return ARM_IMAGE
        return X86_IMAGE

    def pull_image(self):
        """Pull the selenium image"""
        self.client.images.pull(self.image)

    def run_container(self):
        """Run the selenium image in a container"""
        self.container = self.client.containers.run(
            self.image,
            auto_remove=True,
            detach=True,
            shm_size="2g",
            ports={"4444/tcp": 4444},
        )

        # Ensure selenium api is responsive
        for i in range(5):
            try:
                with urllib.request.urlopen("http://localhost:4444/") as page:
                    if page.getcode() == 200:
                        break
            except (http.client.RemoteDisconnected, urllib.error.URLError):
                pass
            if i == 4:
                raise RuntimeError(
                    "Selenium Docker API did not return a 200 code within 5 seconds"
                )
            time.sleep(1)

        # Ensure chrome driver is responsive
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        for i in range(10):
            try:
                with webdriver.Remote(
                    command_executor="http://localhost:4444/wd/hub", options=options
                ) as _:
                    break
            except urllib3.exceptions.ProtocolError:
                pass
            if i == 4:
                raise RuntimeError("Chrome Docker API did not respond within 5 seconds")
            time.sleep(1)

    def rm_container(self):
        """Remove the container"""
        self.container.remove(force=True)

    @staticmethod
    def install_and_launch_docker():
        """Static method to ensure docker is installed and running.
        If not then it will attempt to rectify the problems
        """
        # Check docker is installed
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except FileNotFoundError as exc:
            logger.info(
                "Docker is not installed properly on your system. Attempting to install with brew"
            )
            # Check brew is installed
            brew_version = subprocess.run(
                ["brew", "--version"], check=True, capture_output=True
            )
            if brew_version.returncode != 0:
                notification_text = (
                    "Brew is not installed, so docker cannot be installed automatically. "
                    "Consider installing https://brew.sh/ or go to docker website to download "
                    "https://docs.docker.com/desktop/install/mac-install/"
                )
                logger.warning(notification_text)
                os.system(
                    f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                            default button "OK" with icon 2'"""
                )
                raise DockerHandlerException(notification_text) from exc
            user_confirm = input(
                "\nDocker is not installed.\n"
                "Would you like to attempt to install docker using brew? [y/N]:"
            )
            if user_confirm.lower() != "y":
                raise DockerHandlerException(
                    "Docker installation aborted by user"
                ) from exc
            logger.info("Installing docker with brew")
            subprocess.run(
                ["brew", "install", "--cask", "docker"],
                check=True,
                capture_output=False,
            )
            # Unfortunately docker needs to be launched from finder first time to finish the setup
            notification_text = (
                "Docker was installed with brew. To finish the docker setup, "
                "run the docker application from within your Applications folder (will open automatically)"
            )
            os.system(
                f"""osascript -e 'display dialog "{notification_text}" with title "TP Timesheet" buttons "OK" \
                        default button "OK" with icon 2'"""
            )
            os.system("open /Applications")
            sys.exit(0)

        # Launch docker engine, does nothing if already running
        docker_open = subprocess.run(
            ["open", "--hide", "--background", "-a", "Docker"],
            check=False,
            capture_output=True,
        )
        if docker_open.returncode != 0:
            # Something unexpected happened. Capture stderror
            raise DockerHandlerException(docker_open.stderr.decode().strip())

        # Check docker engine is running. Timeout after 30 seconds
        for _ in range(15):
            docker_stats = subprocess.run(
                ["docker", "stats", "--no-stream"], check=False, capture_output=True
            )
            if docker_stats.returncode == 0:
                return
            logger.debug("Waiting for docker engine to spool up")
            time.sleep(2)

        # Docker engine timed out
        raise DockerHandlerException(
            "Docker engine is unresponsive. Please check your docker install"
        )
