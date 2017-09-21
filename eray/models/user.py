import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

from eray.models.achievements import Achievement
from eray.models.content import (BaseVote, Question, Comment, Answer, BaseComment, Tag, )


def avatar_directory(instance, filename):
    return '/'.join(['avatars', str(datetime.datetime.now().year), str(datetime.datetime.now().month), filename])

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=avatar_directory)
    achievements = models.ManyToManyField(Achievement)

    #notification settings
    notify_instant = models.BooleanField(default=False)
    notify_hourly = models.BooleanField(default=False)
    notify_daily = models.BooleanField(default=True)
    notify_weekly = models.BooleanField(default=False)

    notify_comment = models.BooleanField(default=True)
    notify_answer = models.BooleanField(default=True)    

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

    def get_voted_answers(self, answer_list=False):
        """Retrieve a dictionary with all answers the user voted on

        If answer_list is provided, only the intersection of answer_list 
        and the answers the user voted on will be returned
        """
        base_votes = BaseVote.objects.filter(user__profile=self).exclude(parent__answer__isnull=True).select_related('parent', 'parent__answer')
        if answer_list:
            base_votes = base_votes.filter(parent__answer__in=answer_list)

        voted_answers = {
            'positive_votes': [],
            'negative_votes': [],
        }

        for vote in base_votes:
            if vote.value > 0:
                voted_answers['positive_votes'].append(vote.parent.answer)
            else:
                voted_answers['negative_votes'].append(vote.parent.answer)

        return voted_answers

    def get_voted_questions(self, question_list=False):
        """Retrieve a dictionary with all questions the user voted on

        If question_list is provided, only the intersection of question_list 
        and the questions the user voted on will be returned
        """
        base_votes = BaseVote.objects.filter(user__profile=self).exclude(parent__question__isnull=True).select_related('parent', 'parent__question')
        if question_list:
            base_votes = base_votes.filter(parent__question__in=question_list)

        voted_questions = {
            'positive_votes': [],
            'negative_votes': [],
        }

        for vote in base_votes:
            if vote.value > 0:
                voted_questions['positive_votes'].append(vote.parent.question)
            else:
                voted_questions['negative_votes'].append(vote.parent.question)

        return voted_questions


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


class UserNotificationStream(models.Model):
    """Notification log
    """
    NOTIFICATION_TYPES = (
        ('NEW_ANSWER', 'NEW_ANSWER'),
        ('NEW_COMMENT', 'NEW_COMMENT'),
        ('ANSWER_ACCEPTED', 'ANSWER_ACCEPTED'),
        ('NEW_QUESTION', 'NEW_QUESTION'),
    )

    user = models.ForeignKey(User)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)


class UserSubscribedQuestion(models.Model):
    """Questions an User is subscribed to
    """
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)


class UserSubscribedTag(models.Model):
    """Tags an User is subscribed to
    """
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
