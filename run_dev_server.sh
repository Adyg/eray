#!/bin/bash
cd /vagrant
printf "Installing requirements ...\n"
pip install -r requirements/local.txt

printf "Running collectstatic ...\n"
/usr/bin/python manage.py collectstatic --noinput --settings=eray.settings.local
printf "Starting server on the box's port 8001 ...\n"
/usr/bin/python manage.py runserver [::]:8001 --settings=eray.settings.local