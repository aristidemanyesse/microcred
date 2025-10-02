#!/bin/bash
# weed mount -filer="fs-filer-1:8888,fs-filer-2:8888,fs-filer-3:8888" -nonempty -dataCenter="jdc.1" -dir=/vfs -filer.path=/jool/back -allowOthers &
service cron start
# yes | python manage.py makemigrations
yes | python manage.py migrate
python manage.py crontab add
python manage.py runserver 0.0.0.0:8000
