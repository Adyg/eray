import datetime

from django.contrib.auth.models import User
from django.db import models


class Achievement(models.Model):
    """Achievements are automatically created.

    Check the achievements module for the currently enabled achievements.
    """
    title = models.CharField(max_length=300)
    description = models.TextField()
    slug = models.CharField(max_length=300)

