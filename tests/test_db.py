import pytest
import pytest_asyncio
from src.db import Database
from datetime import datetime


@pytest_asyncio.fixture
async def test_db(db_config):
    database = Database(dsn=db_config)
    await database.connect()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_log_failure(test_db):

    test_url = 'https://unexistedwebsite.com'
    test_response_time = 1.23
    test_status_code = 404
    test_error_message = 'test error message'

    await test_db.log_failure(test_url, datetime.now(), test_response_time, test_status_code, test_error_message)
    result = await test_db.pool.fetch('SELECT * FROM failed_requests')
    assert len(result) == 1
    assert result[0]['id'] == 1
    assert result[0]['response_time'] == 1.23
    assert result[0]['url'] == test_url
    assert result[0]['status_code'] == test_status_code
    assert result[0]['error_message'] == test_error_message
