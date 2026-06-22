#!/bin/bash
set -e
python manage.py migrate --noinput
python manage.py seed_data 2>/dev/null || true
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
