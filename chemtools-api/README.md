# Chemtools API

## Installation

1. Create `.env` file from `.env.template` and change neccessary variables
2. Run `poetry install`

## Run locally
```bash
docker compose up --build
```


## TODOs

- install isort, precommit hook
- push to ncbr repo (maybe use gitmodules to have them together on my gitlab)
- auth + MUNI jednotne prihlaseni
- add cron health check tests which check whether charge works (on small molecule file)

- Mole - mono
    - create dockerfile for mole using mono
    - mole is using xml for input
