import os

from logger import logger
from monitor import monitor_url
from db import Database
import load_config
import asyncio
from asyncio import Event

import signal

"""
Author: Jonathan Kalma
https://github.com/jonathanyk
"""


def signal_handler(stop_event: Event):
    def handler():
        logger.info("=-= STOPPING MONITOR APP -=-")
        stop_event.set()

    return handler


async def main():
    config = load_config.load_config()
    start_msg = "=-= STARTING MONITOR APP =-="
    logger.info(start_msg)

    db = Database(dsn=os.getenv('DATABASE_URL'))
    await db.connect()

    max_workers = int(os.getenv('MAX_WORKERS'))
    stop_event = asyncio.Event()

    # Register signal handler
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler(stop_event))

    monitor_task = asyncio.create_task(monitor_url(db, config, stop_event, max_workers))

    await stop_event.wait()
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    await db.close()
    logger.info("=-= MONITOR APP STOPPED =-=")


if __name__ == '__main__':
    asyncio.run(main())
