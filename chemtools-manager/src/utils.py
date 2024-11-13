import yaml


def load_yml(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
