import logging
from logger import logger
import asyncpg
from typing import Optional


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        #self.pool = None

    # handle db connection executions
    async def execute_query(self, query: str, *args: any) -> None:
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(query, *args)
        except asyncpg.PostgresConnectionError as ex:
            logging.error(f"db connection error occurred: {ex}")
        except asyncpg.PostgresError as ex:
            logging.error(f"db error occurred: {ex}")
        except Exception as e:
            logging.error(f"error occurred: {e}")

    # init db with dedicated table to store monitoring logs
    async def init_db(self) -> None:
        await self.execute_query('''CREATE TABLE IF NOT EXISTS failed_requests (
                                      id SERIAL PRIMARY KEY,
                                      url TEXT NOT NULL,
                                      timestamp TIMESTAMPTZ NOT NULL,
                                      response_time FLOAT NOT NULL,
                                      status_code INT NOT NULL,
                                      error_message TEXT
                           )''')

    # handle failures - log both in db console and log file
    async def log_failure(self, url: str, timestamp: str, response_time: float, status_code: int,
                          error_msg: Optional[str] = None) -> None:
        await self.execute_query(
            '''INSERT INTO failed_requests(url, timestamp, response_time, status_code, error_message)
               VALUES($1, $2, $3, $4, $5)''',
            url, timestamp, response_time, status_code, error_msg
        )

        error_desc = (f"MONITORING FAILURE -- url: {url}  |  "
                      f"timestamp:{timestamp}  |  "
                      f"response_time:{response_time}  |  "
                      f"returned status code:{status_code}  |  "
                      f"error description:{error_msg}")

        logger.error(error_desc)

    # log success requests to log file
    async def log_success(self, url: str, timestamp: str, response_time: float, status: int,
                          is_pattern_located: bool = False) -> None:
        log_desc = (f"monitoring -- url: {url}  |  "
                    f"timestamp:{timestamp}  |  "
                    f"response_time:{response_time}  |  "
                    f"returned status code:{status}  |  "
                    f"pattern located:{is_pattern_located}")
        logger.info(log_desc)

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        await self.init_db()

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
