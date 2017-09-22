from django import template

from eray.lib.eray_paginator import ErayPaginator
from eray.models.user import (UserSubscribedQuestion, UserSubscribedTag, )

register = template.Library()


def subscriptions(context, profile):
    """Output the subscriptions for the profile
    Only if it's the user viewing their own profile
    """
    question_subscriptions = []
    tag_subscriptions = []

    if context.request.user.is_authenticated() and context.request.user == profile.user:
        question_subscriptions = profile.get_question_subscriptions()
        tag_subscriptions =  profile.get_tag_subscriptions()


    response = {
        'question_subscriptions': question_subscriptions,
        'tag_subscriptions': tag_subscriptions,
      }

    return response


register.inclusion_tag('eray/tag_templates/_subscriptions.html', takes_context=True)(subscriptions)
