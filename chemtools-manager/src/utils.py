from pathlib import Path
import tomllib
import yaml

ROOT_DIR = Path(__file__).parent.parent.resolve()
LOGGING_PATH = ROOT_DIR / "logs/logger.log"


def load_yml(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_project_version():
    pyproject_path = ROOT_DIR / "pyproject.toml"
    with open(pyproject_path, "rb") as file:
        return tomllib.load(file)["tool"]["poetry"]["version"]
