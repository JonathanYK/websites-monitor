## Monitoring URL App

**Asynchronous Website Monitoring Tool**

* Monitors website availability and response times.
* Uses asynchronous programming for efficient performance.
* Logs failures in a PostgreSQL database.
* Records successful requests in a separate log file.

### Configuration
* **config/config.yaml:**
  * List of URLs with address, testing interval, and optional regex.
* **.env:**
  | Variable | Description | Default |
  |---|---|---|
  | `CONFIG_FILE_PATH` | Path to `config/config.yaml` | Mandatory |
  | `POSTGRES_USER` | PostgreSQL username (optional) | `postgres` |
  | `POSTGRES_PASSWORD` | PostgreSQL password (optional) | `postgres` |
  | `POSTGRES_DB` | Database name (optional) | `monitordb` |
  | `MAX_WORKERS` | Maximum concurrent workers (optional) | `10` |
  | `MIN_INTERVAL_VAL` | Minimum check interval (seconds, optional) | `2` |
  | `MAX_INTERVAL_VAL` | Maximum check interval (seconds, optional) | `10` |

### Running the Application
* Use `docker-compose up` to start the application:
  * `postgresdb` container for the database.
  * `monitoring_app` container for the monitoring application.

### Technical Stack
* Python (3.x)
* asyncpg
* asyncio
* aiohttp
* psycopg2 (optional)
* Docker Compose
* testcontainers (testing)
* pytest
* pytest-asyncio

### Code Structure
* **main.py:** Application initialization, database connection, URL monitoring, signal handling.
* **db.py:** Asynchronous database interactions, connection pool, table creation, logging.
* **monitor.py:** URL fetching, processing, monitoring loops.
* **docker-compose.yml:** Defines database and monitoring app services.
* **wait-for-it.sh:** Ensures database readiness.
* **.env.test & conftest.py:** Test environment configuration.
* **test_db.py:** Database and logging unit tests.
