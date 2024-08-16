
### Python application that monitors website availability and response times asynchronously.<br> It uses `asyncpg` for asynchronous PostgreSQL interactions and Python's `asyncio` package to concurrently execute the `monitor_url` method using the Semaphore class that pre-define the amount of concurrent workers. <br> Failed requests are logged in a PostgreSQL database, while successful requests are recorded in a `monitor.log` file. This setup ensures efficient monitoring and logging for website performance tracking.

### configuration and execution
* `config/config.yaml` should include urls list, where each url will have it's  address, interval of testing (seconds) and the regex to search for (optional)
* `.env` should include the following keys (.env file attached for reference):
  * `CONFIG_FILE_PATH` - mandatory, path to `config/config.yaml`
  * `POSTGRES_USER` - optional, default is `postgres`
  * `POSTGRES_PASSWORD` - optional, default both for user and password is `postgres`
  * `POSTGRES_DB` - optional, default is `monitordb`
  * `MAX_WORKERS` - optional param to set the concurrent workers that would execute monitor, default is `10`
  * `MIN_INTERVAL_VAL` - optional, default is `2`
  * `MAX_INTERVAL_VAL` - optional, default is `10`

* `docker-compose up` will create 2 containers - `postgresdb` for database and `monitoring_app` for the monitoring application, so the application will integrate and log the failures to that db
* `wait-for-it.sh` script that will ensure that `postgresdb` container will start and finish init before `monitoring_app` starts

<br>

### Technical description:
#### main.py:
Initializes the monitor application which connects to postgres db using an environment variable for .env, loads configuration settings, and monitors multiple URLs concurrently with asynchronous tasks.
It handles termination signals to gracefully stop the monitoring process. The script uses asyncio for asynchronous programming, managing tasks, and handling signals for a clean shutdown.

#### db.py:
handles asynchronous database interactions using asyncpg, connects to a PostgresSQL database containe and creating a connection pool.  
* `init_db` method will ensure that the table for storing monitoring logs exists.
* `execute_query` method handles the execution of database queries, ensuring proper error logging.
* `log_failure` method logs monitoring failures into the database and logs the error.
* `log_success` method logs successful requests. The close method closes the database connection pool.

#### monitor.py:
* `fetch` method executes asynchronous HTTP GET requests using aiohttp, calculates response time, and handles exceptions.
* `worker` method processes a single URL task, logging failures to the database and successes to a log file.
* `monitor_url` method monitors URLs at specified intervals using the `fetch` method, logs failures to the database, logs successes to a log file, and loops indefinitely until a stop event is triggered.


#### docker-compose.yml
* `db` service runs PostgresSQL database, configured with env variables from .env file.
* `app` service builds a Docker image from the monitoring app Dockerfile, and configures to work with `db` container that already created, and executes `wait-for-it.sh` to ensure that db will be ready before `app` execution.

#### wait-for-it.sh:
* Waits for PostgreSQL to become available before executing `app` container, retrying until a timeout is reached, uses netcat for the connection check.
<br>

#### Tests:
* `.env.test` Similar to .env but for testing environment (attached for reference as well)


#### conftest.py
* `postgres_container` method uses testcontainers to start a PostgresSQL container for the test session, in order to integrate with the test.\
* `db_config` using pytest_asyncio to fetch the URL from the running PostgresSQL container and adjusting it for asyncpg.

#### test_db.py
* `test_db` method creates Database instance, and connects to db.\
* `test_log_failure` method logs a failure entry for https://unexistedwebsite.com into db using the log_failure method. this test ensures that the log_failure method logs failures to database correctly.

















