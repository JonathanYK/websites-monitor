FROM python:3.10-slim

WORKDIR /app

# Install netcat for wait-for-it.sh script
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy the wait-for-it script to the container
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY /src /src
COPY requirements.txt .
COPY .env .
COPY /config /config

RUN pip install --no-cache-dir -r requirements.txt

CMD ["/wait-for-it.sh", "db:5432", "--", "python", "src/main.py"]
