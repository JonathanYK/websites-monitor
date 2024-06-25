import os
import sys
import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from src.load_config import load_config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


@pytest.fixture(scope="session")
def postgres_container():
    load_config(dotenv_path='../.env.test')
    container = PostgresContainer("postgres:latest")
    container.start()
    yield container
    container.stop()


@pytest_asyncio.fixture(scope="session")
async def db_config(postgres_container):
    dsn = postgres_container.get_connection_url()
    dsn = dsn.replace('postgresql+psycopg2', 'postgresql')
    return dsn
