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

    def toggle_subscribe_question(self, question):
        """Toggle subscription of a user to a Question
        """
        UserSubscribedQuestion.toggle(user=self.user, subscribed_obj=question)

    def toggle_subscribe_tag(self, tag):
        """Toggle subscription of a user to a Tag
        """
        UserSubscribedTag.toggle(user=self.user, subscribed_obj=tag)

    def is_subscribed_to_question(self, question):
        """Check if the user is subscribed to a question
        """

        return UserSubscribedQuestion.is_subscribed(self.user, question)

    def get_question_subscriptions(self):
        """Retrieve all the questions an user is subscribed to
        """

        return UserSubscribedQuestion.get_subscriptions(self.user)

    def get_tag_subscriptions(self):
        """Retrieve all the tags an user is subscribed to
        """

        return UserSubscribedTag.get_subscriptions(self.user)

    def is_subscribed_to_tag(self, tag):
        """Check if the user is subscribed to a Tag
        """

        return UserSubscribedTag.objects.filter(subscribed_obj=tag, user=self.user).exists()

    def is_subscribed_to_question(self, question):
        """Check if the user is subscribed to a Question
        """

        return UserSubscribedQuestion.objects.filter(subscribed_obj=question, user=self.user).exists()


class UserActionStreamManager(models.Manager):
    def create(self, *args, **kwargs):
        #ensure no duplicate notifications
        filters = {
            'user': kwargs['user'],
            'action_type': kwargs['action_type'],
        }
        if 'question' in kwargs:
            filters['question'] = kwargs['question']
        if 'answer' in kwargs:
            filters['answer'] = kwargs['answer']
        if 'comment' in kwargs:
            filters['comment'] = kwargs['comment']

        try:
            self.get(**filters)
        except:

            return super(UserActionStreamManager, self).create(*args, **kwargs)  

        return False


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

    objects = UserActionStreamManager()

    @classmethod
    def handle_new_action(cls, **kwargs):
        stream_item = False

        # avoid duplicate notifications
        try:
            stream_item = cls.objects.get(**kwargs)
        except:
            stream_item = cls.objects.create(**kwargs)

        return stream_item


class UserNotificationStream(models.Model):
    """Notification log
    """
    NOTIFICATION_TYPES = (
        ('NEW_ANSWER', 'NEW_ANSWER'),
        ('NEW_COMMENT', 'NEW_COMMENT'),
        ('ANSWER_ACCEPTED', 'ANSWER_ACCEPTED'),
        ('NEW_QUESTION', 'NEW_QUESTION'),
    )

    ACTION_TO_NOTIFICATION = {
        'ASK': 'NEW_QUESTION',
        'ANSWER': 'NEW_ANSWER',
        'COMMENT': 'NEW_COMMENT',
        'ACCEPTED': 'ANSWER_ACCEPTED',
        'WAS_ACCEPTED': 'ANSWER_ACCEPTED',
    }

    NOTIFICATION_STATUS = (
        ('P', 'Pending'),
        ('E', 'Sending'),
        ('S', 'Sent'),
        ('F', 'Failed'),
    )

    user = models.ForeignKey(User)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    notification_status = models.CharField(max_length=1, choices=NOTIFICATION_STATUS, default='P', db_index=True,)

    @classmethod
    def notify_new_answer(cls, answer, action_type):
        subscriptions = UserSubscribedQuestion.get_subscribers([answer.parent, ])

        for subscription in subscriptions:
            cls.add_notification(user=subscription.user,
                                question=answer.parent,
                                notification_type=cls.ACTION_TO_NOTIFICATION[action_type])

    @classmethod
    def notify_new_question(cls, question, action_type):
        subscriptions = UserSubscribedTag.get_subscribers(question.tags.all())

        for subscription in subscriptions:
            cls.add_notification(user=subscription.user,
                                question=question,
                                tag=subscription.subscribed_obj,
                                notification_type=cls.ACTION_TO_NOTIFICATION[action_type])

    @classmethod
    def add_notification(cls, **kwargs):
        notification_item = False

        # avoid duplicate notifications
        try:
            notification_item = cls.objects.get(**kwargs)
        except:
            notification_item = cls.objects.create(**kwargs)

        return notification_item

    @classmethod
    def update_status(cls, notifications_qs, status, **kwargs):
        notifications_qs.update(notification_status=status)
       
    @classmethod
    def prepare_notification_batch_for_sending(cls, **kwargs):
        NOTIFICATION_BATCH_SIZE = 10

        notifications = cls.objects.filter(notification_status='P').select_related('user', 'question', 'tag')[0:NOTIFICATION_BATCH_SIZE]
        notification_pks = [notification.pk for notification in notifications]
        #cls.update_status(cls.objects.filter(pk__in=notification_pks), 'E')

        return notifications

    def mark_sent(self):

        #self.notification_status = 'S'
        self.save()

class ToggleableSubscription(models.Model):

    class Meta:
        unique_together = ('user', 'subscribed_obj', )
        abstract = True

    @classmethod
    def toggle(self, user, subscribed_obj):
        """If a subscription exists, remove it. If not, create it
        """
        subscription = False
        try:
            subscription = self.objects.get(user=user, subscribed_obj=subscribed_obj)
        except:
            pass

        if subscription:
            subscription.delete()

            return False

        subscription = self.objects.create(user=user, subscribed_obj=subscribed_obj)

        return True

    @classmethod
    def is_subscribed(self, user, subscribed_obj):
        """Check if a subscription exists
        """

        return self.objects.filter(user=user, subscribed_obj=subscribed_obj).exists()

    @classmethod
    def get_subscriptions(self, user):

        return self.objects.filter(user=user).select_related('subscribed_obj')

    @classmethod
    def get_subscribers(self, subscribed_objs):

        return self.objects.filter(subscribed_obj__in=subscribed_objs).select_related('user')


class UserSubscribedQuestion(ToggleableSubscription):
    """Questions an User is subscribed to
    """
    user = models.ForeignKey(User)
    subscribed_obj = models.ForeignKey(Question)


class UserSubscribedTag(ToggleableSubscription):
    """Tags an User is subscribed to
    """
    user = models.ForeignKey(User)
    subscribed_obj = models.ForeignKey(Tag)
