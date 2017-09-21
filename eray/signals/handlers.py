from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from eray.models.content import (Question, BaseComment, Answer,)
from eray.models.user import (UserActionStream, )

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
    UserActionStream.objects.create(user=instance.user, question=instance, action_type='ASK')

@receiver(post_save, sender=BaseComment)
def create_comment(sender, instance, created, **kwargs):
    UserActionStream.objects.create(user=instance.user, comment=instance, action_type='COMMENT')

@receiver(post_save, sender=Answer)
def create_answer(sender, instance, created, **kwargs):
    if instance.user:
        UserActionStream.objects.create(user=instance.user, answer=instance, action_type='ANSWER')
    elif instance.accepted:
        # add Accepted actions to the action streams of both asker and answerer
        UserActionStream.objects.create(user=instance.user, answer=instance, action_type='WAS_ACCEPTED')
        UserActionStream.objects.create(user=instance.parent.user, answer=instance, action_type='ACCEPTED')
