from __future__ import absolute_import
from .celery import app as celery_app

default_app_config = 'eray.apps.ErayConfig'
__all__ = ['celery_app']