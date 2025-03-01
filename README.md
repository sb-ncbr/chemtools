# Chemtools Manager

## How to run the project locally

### Installation

- Copy `template.env` to `.env` and adjust environment variables as needed
- Run `poetry install`
- Run `docker compose build`

### Run Chemtools API

- Run `docker compose up` (This runs postgres, rabbitmq, minio, and the API)
- Run `cd src && ../bin/run_worker.sh` (This runs worker from the `src/` directory)


## TODO

- gesamt - podpora -s/-d \[kinda done\]
- gesamt - later finish output parsing for multiple files (more than 3)
- make mole great (working) again
- db setup including calculation_id and order, user is just a token

- write about command injection (_get_cmd_args)
- solve issue with non existing docker directory structure
