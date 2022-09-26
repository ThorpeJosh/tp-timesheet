""" Handler for running selenium and chrome backend """
import platform
import docker
from time import sleep

ARM_IMAGE = 'seleniarm/standalone-chromium:105.0'
X86_IMAGE = 'selenium/standalone-chrome:105.0'

class DockerHandler:
    """ Docker handler """

    def __init__(self):
        self.client = docker.from_env()
        self.arch = platform.machine()
        self.image = self.select_image(self.arch)
        self.container = None

    @staticmethod
    def select_image(arch):
        """ Select the correct image based on the client architecture """
        if arch == 'arm64':
            return ARM_IMAGE
        else:
            return X86_IMAGE

    def pull_image(self):
        """ Pull the selenium image """
        self.client.images.pull(self.image)

    def run_container(self):
        """ Run the slenium image in a container """
        self.container = self.client.containers.run(self.image, auto_remove=True, detach=True, shm_size='2g', ports={'4444/tcp':4444})
        # wait for container to run
        timeout = 5
        stop_time = 0.5
        elasped_time = 0
        while self.container.status != 'running' and elasped_time < timeout:
            sleep(stop_time)
            elasped_time += stop_time
            continue

    def rm_container(self):
        """ Remove the container """
        self.container.remove(force=True)
