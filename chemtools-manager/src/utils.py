import yaml
from dependency_injector.wiring import Provide
from fastapi import Depends

from containers import ApplicationContainer


def load_yml(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def from_app_container(attr_name: str):
    return Depends(Provide[getattr(ApplicationContainer, attr_name)])
