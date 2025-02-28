from pathlib import Path
import tomllib
from typing import Callable
from zipfile import ZipFile
import yaml

from fastapi import File

ROOT_DIR = Path(__file__).parent.parent.resolve()
LOGGING_PATH = ROOT_DIR / "logs/logger.log"


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
