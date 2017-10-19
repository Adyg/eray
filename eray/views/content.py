from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Sum, Q, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from haystack.query import SearchQuerySet

from eray.models.content import (Question, Tag, )
from eray.lib.eray_paginator import ErayPaginator


@login_required
def subscribe_question(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    request.user.profile.toggle_subscribe_question(question)

    return HttpResponse('')

@login_required
def subscribe_tag(request, tag_pk):
    tag = get_object_or_404(Tag, pk=tag_pk)
    request.user.profile.toggle_subscribe_tag(tag)

    return HttpResponse('')


def tag_details(request, tag):
    """ Tag details page
    Listing the tag description along with example content tagged with it
    """
    tag = get_object_or_404(Tag, name=tag)

    related_questions = tag.questions.all().order_by('-created_at')[:5]

    try:
        is_subscribed = request.user.profile.is_subscribed_to_tag(tag)
    except:
        is_subscribed = False

    return render(request, 'eray/tag_details.html', {
        'tag': tag,
        'related_questions': related_questions,
        'is_subscribed': is_subscribed,
    })


def search(request, search_query):
    MAX_RESULTS = 10
    results = SearchQuerySet()
    results = results.filter(text=search_query)
    results_count = results.count()    

    page = request.GET.get('page', 1)
    #results_page = results[search_result_page_size*(page-1):search_result_page_size*page]

    paginator = ErayPaginator(results, MAX_RESULTS)

    try:
        results_page = paginator.page(page)
    except PageNotAnInteger:
        results_page = paginator.page(1)
    except EmptyPage:
        results_page = paginator.page(paginator.num_pages)

    spelling_suggestion = results.spelling_suggestion(search_query)
    # spelling_suggestion is returned in the "text:(suggestion)". Extract the suggestion
    if spelling_suggestion:
        spelling_suggestion = spelling_suggestion.replace('text:(', '').replace(')', '')

    return render(request, 'eray/search.html', {
        'results': results_page,
        'results_count': results_count,
        'search_query': search_query,
        'spelling_suggestion': spelling_suggestion,
    })
