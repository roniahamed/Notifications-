#!/bin/sh
set -e

echo "Running makemigrations..."
python manage.py makemigrations auth_app notifications --noinput
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
