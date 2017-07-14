from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver

from eray.models import (Question, Answer, BaseVote, BaseView)


@receiver(post_save, sender=BaseVote)
def update_question_vote_count_handler(sender, instance=None, created=None, update_fields=None, **kwargs):
    """Each time a Vote is added, updated the denormalized vote count for it's parent Question/Answer
    """
    base_vote = instance
    parent = base_vote.parent.question

    if not parent:
        parent = base_vote.parent.answer
    vote_count = parent.vote_set.all().aggregate(vote_count=Coalesce(Sum('basevote__value'), 0))

    parent.vote_count = vote_count['vote_count']
    parent.save()


@receiver(post_save, sender=BaseView)
def update_question_view_count_handler(sender, instance=None, created=None, update_fields=None, **kwargs):
    """Each time a View is added, updated the denormalized view count for it's parent Question/Answer
    """
    base_view = instance
    parent = base_view.parent.question

    if not parent:
        parent = base_view.parent.answer
    view_count = parent.view_set.all().aggregate(view_count=Coalesce(Sum('baseview__value'), 0))

    parent.view_count = view_count['view_count']
    parent.save()
        