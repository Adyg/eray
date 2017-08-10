import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def avatar_directory(instance, filename):
    return '/'.join(['avatars', str(datetime.datetime.now().year), str(datetime.datetime.now().month), filename])

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=avatar_directory)

    def get_long_name(self):
    	"""Returns the First name and Last name
    	"""

    	return '{} {}'.format(self.user.first_name, self.user.last_name)

    def get_username(self):
    	"""Return the user's username
    	"""

    	return '{}'.format(self.user.username)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()