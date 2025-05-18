# Chemtools Manager

Backend for running calculations using bioinformatics tools in separate Docker containers.
It consists of the **API**, which serves as an entry point, and the **worker**,
which runs the calculations inside the Docker containers.

## How does it work

There are two entry points to the app - the API (`app.py`) and the worker (`worker.py`). The API is responsible for handling user requests, and the worker runs programs utilizing Docker. By running `docker compose up`, you start the app together with the database, RabbitMQ message broker, and the storage. The worker needs to be run separately.  
Firstly, you need to understand that this backend will be used mostly by front-end applications. They have their own worker deployed, and they utilize pipelines. A basic user who just wants to run their independent calculation doesn't need to create any pipeline. At this point, you are ready to upload your first file. You can do so by using a POST files endpoint. Then, you are ready to trigger a calculation run by sending a POST request to any of the available tool endpoints. After that, a message is sent to a queue, from which the worker consumes it. After the calculation ends, you can access the result from the GET calculation endpoint. Finally, to download the result files, you can use the GET files endpoint.

### Architecture

![Archtecture](docs/architecture.svg)

## How to run the project locally
> **NOTE:** Since the worker doesn't run inside a container, it needs to be run locally within a poetry virtual environment. Therefore, you need to be inside a shell (`poetry shell`) or always use the prefix `poetry run` when starting the worker. This also applies to the `alembic` migration utility if you run it from the outside of the *chemtools_api* container.

### Installation

1. Copy `template.env` to `.env` and adjust environment variables as needed
2. Run `poetry install` to install the project locally for the worker (Poetry >=2.0 is required!)
3. Run `docker compose up --build` to build the api along with needed services and start them
4. Run `poetry run alembic upgrade head` to migrate database
5. Set up MinIO locally at `http://127.0.0.1:9001/access-keys` by creating an access key and updating the `.env` file accordingly. *You can skip this step if you store your data in filesystem (using `FilesystemStorageService`)*
6. Build images that will be run by the worker.

### Run

- Run `docker compose up` to start the API, postgres, rabbitmq, and minio
- Run `poetry run python src/worker.py` to start the worker

## Development

### Adding new tools

Follow these steps to add a new tool support:
- Build the tool image
- Create a new directory in `src/tools/` directory next to the other tools, containing three files:
    - `endpoints.py` - Definition of endpoints
    - `schema.py` - Definition of input data schema
    - `tool.py` - Implementation of the specific tool class inheriting from `BaseDockerizedTool`

### Database

- When you make changes in database models, you need to create a new alembic migration. Run `poetry run alembic revision --autogenerate -m <rev_name>`
- To update changes, use `poetry run alembic upgrade head`
