import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

from eray.models.achievements import Achievement
from eray.models.content import (BaseVote, Question, Comment, Answer, BaseComment, )


def avatar_directory(instance, filename):
    return '/'.join(['avatars', str(datetime.datetime.now().year), str(datetime.datetime.now().month), filename])

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=avatar_directory)
    achievements = models.ManyToManyField(Achievement)

    def get_long_name(self):
    	"""Returns the First name and Last name
    	"""

    	return '{} {}'.format(self.user.first_name, self.user.last_name)

    def get_username(self):
    	"""Return the user's username
    	"""

    	return '{}'.format(self.user.username)

    def get_points(self):
        """Return the total points count

        Will include points from both questions and answers
        """

        return BaseVote.objects.filter(user=self.user).aggregate(Sum('value'))['value__sum']

    def get_action_stream(self):
        """Return the action stream for this profile
        """

        return UserActionStream.objects.filter(user=self.user).order_by('-pk').prefetch_related('user', 'question', 
            'answer', 'answer__parent', 'comment', 'comment__parent', 'comment__parent__question', 'comment__parent__answer')


class UserActionStream(models.Model):
    """Actions log
    Tracks all actions for a user
    """
    ACTION_TYPES = (
        ('ASK', 'ASK'),
        ('ANSWER', 'ANSWER'),
        ('COMMENT', 'COMMENT'),
        ('ACCEPTED', 'ACCEPTED'),
        ('WAS_ACCEPTED', 'WAS_ACCEPTED'),
    )

    user = models.ForeignKey(User)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(BaseComment, null=True, blank=True, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES )

    class Meta:
        unique_together = ('user', 'question', 'answer', 'comment', 'action_type', )