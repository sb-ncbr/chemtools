import importlib
import logging
import pkgutil
import tomllib
from typing import TYPE_CHECKING, Any, Callable, Generator
from zipfile import ZipFile

import yaml
from fastapi import File

import tools
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


def to_str(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def unzip_files(file: File) -> dict[str, Callable[[str], bytes]]:
    zip_file = ZipFile(file)
    # .read() surrounded in lambda to avoid storing all file contents in memory.
    # Also name=name is needed to avoid late binding.
    return {name: lambda name=name: zip_file.read(name) for name in zip_file.namelist()}


def get_tool_modules(module_type: str) -> Generator[tuple[str, Callable], None, None]:
    for _, module_name, _ in pkgutil.iter_modules(tools.__path__):
        try:
            yield module_name, importlib.import_module(f"tools.{module_name}.{module_type}")
        except ModuleNotFoundError:
            continue


def init_app_di() -> None:
    from containers import AppContainer

    container = AppContainer()
    container.wire(
        modules=[
            "__main__",
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


def init_logging(settings: "BaseEnvSettings") -> None:
    logging.basicConfig(level=settings.LOG_LEVEL)
    config = load_yml(ROOT_DIR / "src/conf/logger.yml")
    for logger in ["aio_pika", "urllib3", "docker", "aiormq"]:
        logging.getLogger(logger).setLevel(logging.INFO)
    logging.config.dictConfig(config)
