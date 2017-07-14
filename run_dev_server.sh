#!/bin/bash
cd /vagrant_data
/usr/bin/python3 manage.py migrate

printf "Installing requirements ...\n"
pip3 install -r requirements/local.txt

printf "Running collectstatic ...\n"
/usr/bin/python3 manage.py collectstatic --noinput --settings=eray.settings.local
printf "Starting server on the box's port 8001 ...\n"
/usr/bin/python3 manage.py runserver [::]:8001 --settings=eray.settings.local
