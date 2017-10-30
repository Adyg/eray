from celery import shared_task

from eray.models.user import (UserNotificationStream, Profile, )
from eray.models.content import (Question, Tag, )

@shared_task
def send_notification_emails():
    notifications = UserNotificationStream.objects.filter(notification_status='P').select_related('user', 'question', 'tag', )

    for notification in notifications:
        user
