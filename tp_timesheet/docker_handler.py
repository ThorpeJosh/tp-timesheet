""" Handler for running selenium and chrome backend """
import platform
from time import sleep
import http
import urllib
import urllib3
import docker
from selenium import webdriver

ARM_IMAGE = "seleniarm/standalone-chromium:105.0"
X86_IMAGE = "selenium/standalone-chrome:105.0"


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
            sleep(1)

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
            sleep(1)

    def rm_container(self):
        """Remove the container"""
        self.container.remove(force=True)
