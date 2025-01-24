import abc
import asyncio
import logging
import os
import uuid

import aiofiles
import docker
from fastapi import HTTPException

from services.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


class BaseDockerizedTool(abc.ABC):
    image_name = None
    cmd_params = None
    docker_run_kwargs = {}

    def __init__(self, file_storage_service: FileStorageService, docker: docker.DockerClient):
        self._file_storage_service = file_storage_service
        self._docker = docker

        if self.image_name is None:
            raise ValueError(f'image_name must be set in "{self.__class__.__name__}"')

        os.makedirs(os.path.abspath(f"../data/docker/{self.image_name}/in"), exist_ok=True)

    def _get_cmd_params(self, **_) -> str:
        if self.cmd_params is None:
            raise ValueError(f'cmd_params must be set in "{self.__class__.__name__}"')

        return self.cmd_params

    def _get_docker_run_kwargs(self, **_) -> dict:
        return self.docker_run_kwargs

    async def _preprocess(
        self,
        *,
        input_file: str | None = None,
        input_files: list[str] | None = None,
        token: uuid.UUID | None = None,
        **_,
    ) -> uuid.UUID:
        if input_files is None and input_file is None:
            raise ValueError("Either input_files or input_file must be provided")
        if input_file is not None:
            await self.__pull_input_files([input_file])
        if input_files is not None:
            await self.__pull_input_files(input_files)

        return token or uuid.uuid4()

    async def _postprocess(self, *, _output: str, **kwargs) -> str:
        file_names_to_push = self._get_output_files(_output=_output, **kwargs)
        await self._push_output_files(file_names=file_names_to_push, **kwargs)
        return _output

    async def __pull_input_files(self, file_names: list[uuid.UUID]) -> None:
        for file_name in file_names:
            file_bytes = await self._file_storage_service.fetch_file(file_name)
            file_path = f"../data/docker/{self.image_name}/in/{file_name}"
            async with aiofiles.open(file_path, "wb") as file:
                await file.write(file_bytes)

    async def _push_output_files(self, token: uuid.UUID, file_names: list[str]) -> None:
        for file_name in file_names:
            file_path = f"../data/docker/{self.image_name}/out/{token}/{file_name}"
            async with aiofiles.open(file_path, "rb") as file:
                file_bytes = await file.read()
            await self._file_storage_service.save_file(file_name, file_bytes)

    async def run(self, **kwargs) -> str:
        token = await self._preprocess(**kwargs)
        cmd_params = self._get_cmd_params(token=token, **kwargs)

        logger.debug(f"Running docker container: {self.image_name} {cmd_params}")
        try:
            calculation_result = await asyncio.to_thread(
                self._docker.containers.run,
                self.image_name,
                cmd_params,
                **self._get_docker_run_kwargs(**kwargs),
            )
        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {e}")
            raise HTTPException(status_code=400, detail=self._get_error(e.stderr.decode("utf-8")))

        try:
            return await self._postprocess(_output=calculation_result.decode(), token=token, **kwargs)
        except Exception as e:
            logger.error(f"Postprocess error: {e}")
            raise HTTPException(status_code=500, detail="An error occurred during postprocessing")
