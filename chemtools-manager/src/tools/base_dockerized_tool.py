import abc
import logging
from logging import Logger

import docker
from fastapi import HTTPException


logger = logging.getLogger(__name__)


class BaseDockerizedTool(abc.ABC):
    image_name = None
    cmd_params = None
    docker_run_kwargs = {}

    def __init__(self, docker: docker.DockerClient, logger: Logger):
        self._docker = docker
        self._logger = logger

        if self.image_name is None:
            raise ValueError(f'image_name must be set in "{self.__class__.__name__}"')

    def get_cmd_params(self, *args, **kwargs) -> str:
        if self.cmd_params is None:

            raise ValueError(f'cmd_params must be set in "{self.__class__.__name__}"')

        return self.cmd_params

    def get_docker_run_kwargs(self, *args, **kwargs) -> dict:
        return self.docker_run_kwargs

    def run(self, *args, **kwargs) -> str:
        try:
            output = self._docker.containers.run(
                self.image_name,
                self.get_cmd_params(*args, **kwargs),
                **({"detach": True} | self.get_docker_run_kwargs(*args, **kwargs)),
            )
        except docker.errors.ContainerError as e:
            self._logger.error(f"ContainerError: {e}")
            raise HTTPException(status_code=400, detail=f"Charge calculation failed: {e.stderr.decode("utf-8")}")

        return output.decode("utf-8")
