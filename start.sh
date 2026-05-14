#!/bin/bash
service cron start
yes | python manage.py migrate
yes | python manage.py collectstatic --noinput
python manage.py crontab add
exec gunicorn settings.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
