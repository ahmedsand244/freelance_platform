#!/usr/bin/env bash
set -o errexit

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install specific dependencies needed for Render.com deployment
pip install gunicorn daphne whitenoise dj-database-url psycopg2-binary redis

# Run static files collection and database migrations
python manage.py collectstatic --no-input
python manage.py migrate
