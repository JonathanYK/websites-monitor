from typing import Dict, Any

import yaml
import os
from dotenv import load_dotenv
from logger import logger


def validate_mandatory_env_params():
    default_postgres_user = "postgres"
    default_postgres_password = "postgres"
    default_postgres_db = "monitordb"
    default_max_workers = 10
    default_min_interval = 2
    default_max_interval = 10

    if os.getenv('CONFIG_FILE_PATH') is None:
        logger.error("Missing mandatory environment variable: CONFIG_FILE_PATH")
        exit(1)

    if os.getenv("POSTGRES_USER") is None:
        logger.warning(f"Missing mandatory environment variable: POSTGRES_USER. "
                       f"default {default_postgres_user} will be used.")
        os.putenv('POSTGRES_USER', default_postgres_user)

    if os.getenv("POSTGRES_PASSWORD") is None:
        logger.warning(f"Missing mandatory environment variable: POSTGRES_PASSWORD. "
                       f"default {default_postgres_user} "
                       f"user will be used with default password {default_postgres_password}.")
        os.putenv('POSTGRES_USER', default_postgres_user)
        os.putenv('POSTGRES_PASSWORD', default_postgres_password)

    if os.getenv("POSTGRES_DB") is None:
        logger.warning(f"Missing mandatory environment variable: POSTGRES_DB. "
                       f"default {default_postgres_db} will be used.")
        os.putenv('POSTGRES_DB', default_postgres_db)

    if os.getenv("MAX_WORKERS") is None:
        logger.warning(f"Missing mandatory environment variable: MAX_WORKERS. "
                       f"default {default_max_workers} will be used.")
        os.putenv('MAX_WORKERS', str(default_max_workers))

    if os.getenv("MIN_INTERVAL_VAL") is None:
        logger.warning(f"Missing mandatory environment variable: MIN_INTERVAL_VAL. "
                       f"default {default_min_interval} will be used.")
        os.putenv('MIN_INTERVAL_VAL', str(default_min_interval))

    if os.getenv("MAX_INTERVAL_VAL") is None:
        logger.warning(f"Missing mandatory environment variable: MAX_INTERVAL_VAL. "
                       f"default {default_max_interval} will be used.")
        os.putenv('MIN_INTERVAL_VAL', str(default_max_interval))


def load_config(dotenv_path: str = None) -> Dict[str, Any]:
    load_dotenv(dotenv_path)
    validate_mandatory_env_params()
    with open(os.getenv('CONFIG_FILE_PATH'), 'r') as file:
        config_file = yaml.safe_load(file)

    return config_file
