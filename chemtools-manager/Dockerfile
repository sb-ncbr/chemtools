FROM python:3.13

WORKDIR /code

RUN apt-get update && apt-get install -y postgresql-client

COPY pyproject.toml poetry.lock* ./

RUN pip3 install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

COPY . .

WORKDIR /code/src

CMD ["sh", "-c", "uvicorn app:app --host $APP_HOST --port $APP_PORT"]
