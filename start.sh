#!/usr/bin/env bash

# Start the Celery worker in the background
celery -A khamsat worker -l INFO &

# Start Daphne (ASGI server) in the foreground to serve web requests and websockets
daphne khamsat.asgi:application --port $PORT --bind 0.0.0.0
