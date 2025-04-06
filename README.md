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

1. Copy `template.env` to `.env` and adjust environment variables as needed
2. Run `poetry install` to install project locally for the worker
3. Run `docker compose up --build` to build the api along with needed services and start them
4. Run `poetry run alembic upgrade head` to migrate database
5. Setup MinIO locally by visiting `http://127.0.0.1:9001/access-keys`, creating access key and updating `.env` file accordingly. *You can skip this step if you store your data in filesystem (using `FilesystemStorageService`)*

### Run

- Run `docker compose up` to start the API, postgres, rabbitmq, and minio
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
- To update changes use `poetry run alembic upgrade head`


## TODO

- add list user files endpoint
- add field `force_download` to fetched_file
- save duration for calculation_result.
- SingleFileRequestDto / ManyFilesRequestDto don't forget about this
- setup worker queue names from .env. Remember that each worker should run only 1 queue (possibly more)

- deployment

- write about command injection (_get_cmd_args)
- gesamt - podpora -s/-d \[kinda done\]
- gesamt - later finish output parsing for multiple files (more than 3)
- write docstrings \[in progress\]

- test uploading large files. Maybe it will be necessary to upload/download them by chunks
- write about different architecture possibilities regarding the containerized apps. Each worker runs only one container vs one worker runs every container
- caching -> fetched files -> think of sending head requests to check whether the file on the server has changed. This could be supported only by certain sites. Write about this possible improvement in thesis.
