#!/usr/bin/env bash
# wait-for-it.sh

TIMEOUT=15
if [ $# -eq 0 ]; then
  echo "Usage: $0 host:port [-t timeout]"
  exit 1
fi

HOST=$(echo $1 | cut -d : -f 1)
PORT=$(echo $1 | cut -d : -f 2)
shift 1

while ! nc -z $HOST $PORT; do
  TIMEOUT=$((TIMEOUT-1))
  if [ $TIMEOUT -eq 0 ]; then
    echo "Timeout occurred"
    exit 1
  fi
  echo "Waiting for $HOST:$PORT..."
  sleep 1
done

echo "$HOST:$PORT is up"
exec "$@"
