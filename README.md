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

- Run `docker compose up` (This runs postgres, rabbitmq, minio, and the API)
- Run `cd src && poetry run ../bin/run_worker.sh` (This runs worker from the `src/` directory)

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

- cache
- make mole great (working) again
- create user_file
- save files under name which is hash of the file content
- health endpoint check api, postgres, rabbitmq, and minio
- deployment

- write about command injection (_get_cmd_args)
- gesamt - podpora -s/-d \[kinda done\]
- gesamt - later finish output parsing for multiple files (more than 3)
- write docstrings
- solve issue where I can only run the worker from `src/` folder

- test uploading large files. Maybe it will be necessary to upload/download them by chunks
- thesis idea -> write about invalidating fetched_file cache. Cache can be invalidated just by making a query which deletes the fetched_file records from db.
- how do I ask for more instances on openstack?
