from logger import logger
import os
import re
from datetime import datetime, timedelta
import validators
from typing import Optional


def is_valid_url(url: str) -> bool:
    if not validators.url(url):
        return False
    return True


def is_valid_interval(interval: str) -> bool:
    """Checks if the interval can be converted to int, and between min and max values"""
    try:
        interval_val = int(interval)
        return (isinstance(interval_val, int) and
                int(os.getenv('MIN_INTERVAL_VAL')) <= interval_val <= int(os.getenv('MAX_INTERVAL_VAL')))
    except ValueError:
        return False


def is_valid_regex_pattern(regex_pattern: str, url: str) -> bool:
    """Checks if the regex_pattern is a valid regex_pattern or None"""
    if regex_pattern is None:
        logger.warning(f"regex pattern not defined for url: {url}")
        return True
    try:
        re.compile(regex_pattern)
        return True
    except re.error:
        return False


class Task:
    def __init__(self, url: str, interval: str, regex_pattern: Optional[str] = None):

        if not is_valid_url(url):
            raise ValueError(f"Invalid URL provided: {url}")

        if not is_valid_interval(interval):
            raise ValueError(f"Invalid interval provided for url: {url}")

        if not is_valid_regex_pattern(regex_pattern, url):
            raise ValueError(f"Invalid regex pattern provided for url: {url}")

        self.url = url
        self.interval = interval
        self.regex_pattern = regex_pattern
        self.next_run_time = datetime.now()

    def schedule_next_run(self, timestamp: datetime) -> None:
        self.next_run_time = timestamp + timedelta(seconds=int(self.interval))
