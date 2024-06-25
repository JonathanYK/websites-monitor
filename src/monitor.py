import asyncio
import re
import time
import aiohttp
from datetime import datetime

from aiohttp import ServerDisconnectedError, ClientConnectorError, ClientOSError, ClientResponseError, InvalidURL, \
    TooManyRedirects

from logger import logger
from task import Task
from typing import Tuple, Optional, Any, Dict


async def fetch(session: aiohttp, url) ->  Tuple[Optional[str], Optional[int], float, Optional[str]]:
    start_time = time.perf_counter()
    session_timeout_seconds = 300
    try:
        async with session.get(url, timeout=session_timeout_seconds) as response:
            content = await response.text()
            http_status = response.status
            response_time = time.perf_counter() - start_time
            if http_status == 522:
                return None, http_status, response_time, "Connection timeout error from url"
            return content, http_status, response_time, None

    except (ServerDisconnectedError, ClientConnectorError, ClientOSError, TooManyRedirects, InvalidURL) as e:
        http_status = {
            ServerDisconnectedError: 503,
            ClientConnectorError: 502,
            ClientOSError: 500,
            TooManyRedirects: 310,
            InvalidURL: 400,
        }[type(e)]
        response_time = time.perf_counter() - start_time
        return None, http_status, response_time, e.strerror

    except asyncio.TimeoutError as _:
        response_time = time.perf_counter() - start_time
        http_status = 408  # Timeout error
        return None, http_status, response_time, f'Timeout reached after {session_timeout_seconds} seconds'

    except ClientResponseError as e:
        response_time = time.perf_counter() - start_time
        return None, e.status, response_time, type(e).__name__ + str(e)
    except Exception as e:
        http_status = 500  # Internal Server err
        response_time = time.perf_counter() - start_time
        return None, http_status, response_time, type(e).__name__ + str(e)


async def worker(task: Task, db: Any, semaphore: asyncio.Semaphore) -> None:
    if semaphore.locked():
        logger.warning(f"No free workers available for URL {task.url} at {datetime.now()}")

    else:
        async with aiohttp.ClientSession() as session:
            async with semaphore:
                current_time = datetime.now()
                content, http_status, response_time, error_message = await fetch(session, task.url)
                pattern_found = bool(
                    re.search(task.regex_pattern, content)) if task.regex_pattern and content else False

                if http_status != 200:
                    await db.log_failure(task.url, current_time, response_time, http_status, error_message)

                elif task.regex_pattern and not pattern_found:
                    error_message = f"Pattern:'{task.regex_pattern}' not found"
                    await db.log_failure(task.url, current_time, response_time, http_status, error_message)
                else:
                    await db.log_success(task.url, current_time, response_time, http_status, pattern_found)


async def monitor_url(db: Any, config: Dict[str, Any], stop_event: asyncio.Event, max_workers: int = 5) -> None:
    semaphore = asyncio.Semaphore(max_workers)
    try:
        tasks = [Task(url['url'], url['interval'], url.get('regex')) for url in config['urls']]
    except ValueError as e:
        logger.error(e)
        stop_event.set()
        return

    while not stop_event.is_set():
        while True:
            current_time = datetime.now()
            # find all tasks that are due to run
            due_tasks = [task for task in tasks if task.next_run_time <= current_time]

            if due_tasks:
                # run all due tasks concurrently
                await asyncio.gather(*(worker(task, db, semaphore) for task in due_tasks))

                # schedule the next run of the due tasks
                for task in due_tasks:
                    task.schedule_next_run(current_time)
            else:

                next_run_time = min(task.next_run_time for task in tasks)
                sleep_time = (next_run_time - current_time).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
