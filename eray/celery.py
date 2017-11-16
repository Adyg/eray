from __future__ import absolute_import, unicode_literals
import time
import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eray.settings.local')

app = Celery('eray')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.0, send_notifications.s())

@app.task
def send_notifications():
    from eray.notifications.periodic_notifications import PeriodicNotifications

    PeriodicNotifications.send()
