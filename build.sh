#!/usr/bin/env bash
set -o errexit

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install specific dependencies needed for Railway/Render deployment
pip install gunicorn daphne "whitenoise[brotli]" dj-database-url psycopg2-binary redis channels-redis celery django-redis

# Collect static files (clear old ones first to avoid stale cache)
python manage.py collectstatic --no-input --clear

# Run database migrations
python manage.py migrate
