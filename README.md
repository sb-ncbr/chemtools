# Chemtools Manager

Backend for running calculations using biochemistry tools in separate docker containers.
It consists of the **API**, which serves as an entrypoint, and the **worker**,
which is running the calculations inside the docker containers.

## How does it work (TODO)

### Architecture

![Archtecture](docs/architecture.svg)

## How to run the project locally
> **NOTE:**  Since the worker doesn't run inside a container, it needs to be run locally within a poetry virtual envirnoment. Therefore, you need to be inside a shell (`poetry shell`) or always use prefix `poetry run` when starting the worker. This applies also for the `alembic` migration utility if you run it from the outide of the *chemtools_api* container.

### Installation

- Copy `template.env` to `.env` and adjust environment variables as needed
- Run `poetry install`
- Run `docker compose up --build`
- Run `poetry run alembic upgrade head`

### Run

- Run `docker compose up` to start postgres, rabbitmq, minio, and the API
- Run `poetry run python src/worker.py` to start the worker

## Development

### Adding new tools (TODO write more in detail)
In order to add a new tool, you need to:
- Build the tool image
- Write request schema
- Create new tool class which inherits from `BaseDockerizedTool`
- Extend `DockerizedToolEnum`, which lists supported tools, and prepare 
- Create new endpoint/s for the tool.

### Database

- When you make changes in database models, you need to create new alembic migration. Run `poetry run alembic revision --autogenerate -m <rev_name>`


## TODO

- make mole great (working) again
- deployment

- write about command injection (_get_cmd_args)
- gesamt - podpora -s/-d \[kinda done\]
- gesamt - later finish output parsing for multiple files (more than 3)
- write docstrings \[in progress\]

- test uploading large files. Maybe it will be necessary to upload/download them by chunks
