from django import forms
from django.contrib.auth.models import User

from eray.models.user import Profile


class NotificationForm(forms.ModelForm):
    """Form that handles user notification settings
    """

    class Meta:
        model = Profile
        fields = ['notify_instant', 'notify_hourly', 'notify_daily', 'notify_weekly', 'notify_comment', 'notify_answer', ]

