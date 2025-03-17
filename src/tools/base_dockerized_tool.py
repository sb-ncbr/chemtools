import abc
import logging
import os
import time
import uuid

import docker

from conf.const import ROOT_DIR
from services.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


class ContainerRuntimeError(RuntimeError):
    pass


class BaseDockerizedTool(abc.ABC):
    image_name = None
    cmd_params = None
    docker_run_kwargs = {}

    def __init__(self, file_storage_service: FileStorageService, docker: docker.DockerClient):
        self._file_storage_service = file_storage_service
        self._docker = docker

        if self.image_name is None:
            raise ValueError(f'image_name must be set in "{self.__class__.__name__}"')

    def _get_cmd_params(self, **_) -> str:
        if self.cmd_params is None:
            raise ValueError(f'cmd_params must be set in "{self.__class__.__name__}"')

        return self.cmd_params

    def _get_docker_run_kwargs(self, **_) -> dict:
        return self.docker_run_kwargs

    async def _preprocess(self, *, token: str, input_files: list[str], **_) -> None:
        if not input_files:
            raise ValueError("Either input_files or input_file must be provided")

        os.makedirs(ROOT_DIR / f"data/docker/{self.image_name}/{token}/in", exist_ok=True)
        await self._file_storage_service.download_files(
            input_files, ROOT_DIR / f"data/docker/{self.image_name}/{token}/in"
        )

    async def _postprocess(self, *, _output: str, token: uuid.UUID, **kwargs) -> str:
        file_names_to_push = self._get_output_files(_output=_output, **kwargs)
        await self._file_storage_service.upload_files(
            file_names_to_push,
            ROOT_DIR / f"data/docker/{self.image_name}/{token}/out",
        )
        return _output

    async def run(self, **kwargs) -> str:
        logger.debug(f"Running {self.image_name} tool with kwargs={kwargs}")
        start_time = time.time()

        logger.debug("Invoking preprocess")
        await self._preprocess(**kwargs)

        logger.debug("Obtaining cmd_params")
        cmd_params = self._get_cmd_params(**kwargs)
        logger.debug(f"Obtained cmd_params: {cmd_params}")

        try:
            logger.debug(f"Running docker container: {self.image_name} {cmd_params}")
            calculation_result = self._docker.containers.run(
                self.image_name,
                cmd_params,
                **self._get_docker_run_kwargs(**kwargs),
            )
        except docker.errors.ContainerError as e:
            logger.error(f"Docker run failed on error: {e}")
            raise ContainerRuntimeError(self._get_error(e.stderr.decode("utf-8")))

        try:
            logger.debug("Docker run finished. Invoking postprocess")
            postprocessed_result = await self._postprocess(_output=calculation_result.decode(), **kwargs)
        except Exception as e:
            logger.exception(f"Postprocess error: {e}")
            raise RuntimeError("An error occurred during postprocessing. Please contact the administrator")

        time_total = time.time() - start_time
        logger.info(f"Tool {self.image_name} finished successfully in {time_total:.2f} seconds")
        return postprocessed_result
