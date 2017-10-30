from eray.periodic_tasks.notification_emails import app as celery_app

default_app_config = 'eray.apps.ErayConfig'
__all__ = ['celery_app']