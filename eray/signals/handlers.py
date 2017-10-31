from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from eray.models.content import (Question, BaseComment, Answer,)
from eray.models.user import (UserActionStream, Profile, UserActionStream, UserNotificationStream, )

# Profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# User Action Stream
@receiver(post_save, sender=Question)
def create_question(sender, instance, created, **kwargs):
    UserActionStream.handle_new_action(user=instance.user, question=instance, action_type='ASK')

@receiver(post_save, sender=BaseComment)
def create_comment(sender, instance, created, **kwargs):
    UserActionStream.handle_new_action(user=instance.user, comment=instance, action_type='COMMENT')

@receiver(post_save, sender=Answer)
def create_answer(sender, instance, created, **kwargs):
    if instance.user:
        UserActionStream.handle_new_action(user=instance.user, answer=instance, action_type='ANSWER')
    
    if instance.user and instance.accepted:
        # add Accepted actions to the action streams of both asker and answerer
        UserActionStream.handle_new_action(user=instance.user, answer=instance, action_type='WAS_ACCEPTED')
        UserActionStream.handle_new_action(user=instance.parent.user, answer=instance, action_type='ACCEPTED')

# Notifications
@receiver(post_save, sender=UserActionStream)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        if instance.answer:
            UserNotificationStream.notify_new_answer(instance.answer, instance.action_type)

        if instance.question:
            UserNotificationStream.notify_new_question(instance.question, instance.action_type)            
