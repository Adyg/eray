from eray.models.content import (Question, )
from eray.models.user import (Profile, UserNotificationStream, )
from eray.notifications.senders.email.email_sender import EmailSender

class PeriodicNotifications():
    """Sends periodic notifications
    """
    
    def _prepare_notification_batch():

        return UserNotificationStream.prepare_notification_batch_for_sending()

    @classmethod
    def send(cls):
        notifications = cls._prepare_notification_batch()
        print(notifications)
        for notification in notifications:
            cls._notify_by_email(notification)

    @classmethod
    def _notify_by_email(cls, notification):
        EmailSender.send_notification(notification)