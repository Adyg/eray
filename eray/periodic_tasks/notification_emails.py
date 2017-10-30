from celery import Celery
from celery.schedules import crontab
from celery.contrib import rdb

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Notifications every 1min
    sender.add_periodic_task(60.0, notification_emails.s())

@app.task
def notification_emails():
    rdb.set_trace()
    print('hey hey hey')