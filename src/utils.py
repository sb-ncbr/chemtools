from typing import TYPE_CHECKING
import logging
import tomllib
from typing import Callable
from zipfile import ZipFile

import yaml
from fastapi import File

from conf.const import ROOT_DIR

if TYPE_CHECKING:
    from conf.settings import BaseEnvSettings


def load_yml(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_project_version():
    pyproject_path = ROOT_DIR / "pyproject.toml"
    with open(pyproject_path, "rb") as file:
        return tomllib.load(file)["tool"]["poetry"]["version"]


def unzip_files(file: File) -> dict[str, Callable[[str], bytes]]:
    zip_file = ZipFile(file)
    # .read() surrounded in lambda to avoid storing all file contents in memory.
    # Also name=name is needed to avoid late binding.
    return {name: lambda name=name: zip_file.read(name) for name in zip_file.namelist()}


def init_app_di() -> None:
    from containers import AppContainer

    container = AppContainer()
    container.wire(
        modules=[
            "app",
            "api.routers.io_router",
            "api.routers.system_router",
            "api.routers.tools_router",
            "api.routers.calculations_router",
            "api.routers.pipelines_router",
            "containers",
        ]
    )


def init_worker_di() -> None:
    from containers import WorkerContainer

    container = WorkerContainer()
    container.wire(
        modules=[
            "__main__",
        ]
    )


def init_logging(settings: 'BaseEnvSettings') -> None:
    logging.basicConfig(level=settings.LOG_LEVEL)
    config = load_yml(ROOT_DIR / "src/conf/logger.yml")
    for logger in ["aio_pika", "urllib3", "docker", "aiormq"]:
        logging.getLogger(logger).setLevel(logging.INFO)
    logging.config.dictConfig(config)
