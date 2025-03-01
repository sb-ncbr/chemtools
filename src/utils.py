import logging
import tomllib
from typing import Callable
from zipfile import ZipFile

import yaml
from fastapi import File

from conf.const import ROOT_DIR
from conf.settings import AppSettings


def load_yml(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_project_version():
    pyproject_path = ROOT_DIR / "pyproject.toml"
    with open(pyproject_path, "rb") as file:
        return tomllib.load(file)["tool"]["poetry"]["version"]


def unzip_files(self, file: File) -> dict[str, Callable[[str], bytes]]:
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
            "api.routers.users_router",
            "containers",
        ]
    )


def init_logging(app_settings: AppSettings) -> None:
    logging.basicConfig(level=app_settings.LOG_LEVEL)
    config = load_yml(ROOT_DIR / "src/conf/logger.yml")
    logging.config.dictConfig(config)
