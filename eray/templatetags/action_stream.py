from django import template

from eray.lib.eray_paginator import ErayPaginator
from eray.models.user import UserActionStream

register = template.Library()


def action_stream(context, profile):
    """Output the action stream for a Profile
    """
    MAX_RESULTS = 10

    request = context.request
    page = request.GET.get('page', 1)    
    action_stream_list = profile.get_action_stream()
    paginator = ErayPaginator(action_stream_list, MAX_RESULTS)

    action_stream = []
    try:
        action_stream = paginator.page(page)
    except PageNotAnInteger:
        action_stream = paginator.page(1)
    except EmptyPage:
        action_stream = paginator.page(paginator.num_pages)

    response = {
        'action_stream': action_stream,
        'paginator': paginator,
        'profile': profile,
      }

    return response


register.inclusion_tag('eray/tag_templates/_action_stream.html', takes_context=True)(action_stream)
