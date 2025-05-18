import alembic.config
import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import init_app
from db.database import DatabaseSessionManager
from utils import init_app_di

TEST_DB_NAME = "test_db"
ASYNC_TEST_DB_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5432/{TEST_DB_NAME}"
SYNC_TEST_DB_URL = ASYNC_TEST_DB_URL.replace("+asyncpg", "")


@pytest_asyncio.fixture(autouse=True)
def override_env_vars(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", TEST_DB_NAME)
    monkeypatch.setenv("MINIO_BUCKET", "test-bucket")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def ensure_test_db():
    admin_conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
    dbs = await admin_conn.fetch("SELECT datname FROM pg_database;")
    if not any(row["datname"] == "test_db" for row in dbs):
        await admin_conn.execute(f"CREATE DATABASE {TEST_DB_NAME};")
    await admin_conn.close()


@pytest_asyncio.fixture(scope="function")
async def setup_db():
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", SYNC_TEST_DB_URL)

    alembic.command.downgrade(alembic_cfg, "base")
    alembic.command.upgrade(alembic_cfg, "head")

    db_manager = DatabaseSessionManager()
    db_manager.init(ASYNC_TEST_DB_URL)
    yield db_manager

    alembic.command.downgrade(alembic_cfg, "base")
    await db_manager.close()


@pytest_asyncio.fixture
async def client(setup_db):
    container = init_app_di(test=True)
    app, _ = init_app(container)
    app.container.session_manager = setup_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
