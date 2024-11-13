import dotenv
import os

dotenv.load_dotenv()

# Database settings
POSTGRES_SETTINGS = {
    "postgres_user": os.environ.get("POSTGRES_USER"),
    "postgres_password": os.environ.get("POSTGRES_PASSWORD"),
    "postgres_host": os.environ.get("POSTGRES_HOST"),
    "postgres_port": os.environ.get("POSTGRES_PORT"),
    "postgres_db": os.environ.get("POSTGRES_DB"),
}
POSTGRES_DB_URL = "postgres://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}".format(
    **POSTGRES_SETTINGS
)

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_DB_URL},
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

CHEMTOOLS_MANAGER_CLIENT_URL = os.environ.get("CHEMTOOLS_MANAGER_CLIENT_URL")
