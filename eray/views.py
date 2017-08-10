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

from eray.forms.content import (PostQuestion, PostAnswer, LoginForm, RegistrationForm, )
from eray.models.content import (Tag, Question, Answer,)
from eray.lib.eray_paginator import ErayPaginator


def homepage(request, tags=False):
    """Community question list
    """
    MAX_RESULTS = 10
    page = request.GET.get('page', 1)
    order = request.GET.get('order', False)

    if request.user.is_superuser:
        question_list = Question.all_objects.all()
    elif request.user.is_authenticated:
        question_list = Question.all_objects.filter(Q(status='A') | Q(user=request.user))
    else:
        question_list = Question.all_objects.filter(status='A')

    # filtering by tags
    if tags:
        tags = tags.split(',')
        question_list = question_list.filter(tags__name__in=tags)

    # Coalesce will be used below to avoid NULL values interfering with the ordering
    # Track https://code.djangoproject.com/ticket/10929 for future alternatives
    question_list = question_list.annotate(answer_count=Coalesce(Count('answer'), 0))

    if order:
        if order == 'date':
            question_list = question_list.order_by('-created_at')

        if order == 'votes':
            question_list = question_list.order_by('-vote_count')

        if order == 'views':
            question_list = question_list.order_by('-view_count')

        if order == 'answers':
            question_list = question_list.order_by('-answer_count')

    paginator = ErayPaginator(question_list, 10)

    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    return render(request, 'eray/homepage.html', {
        'questions': questions,
        'date_format': settings.DATE_FORMAT,
        'order': order,
    })


def login(request):
    auth_logout(request)
    login_form = LoginForm()

    # URL the user came from, we'll redirect back to it after login
    next_url = request.GET.get('next', reverse('home'))

    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)

        if login_form.is_valid():
            user = authenticate(username=login_form.cleaned_data[
                                'username'], password=login_form.cleaned_data['password'])

            if user is not None:
                if user.is_active:
                    auth_login(request, user)

                    next_url = request.GET.get('next', reverse('home'))

                    return redirect(next_url)
        else:
            messages.add_message(request, messages.ERROR,
                                 'Login failed. Please check the email and password and try again or use the <a href="#">forgot password</a> form to reset your password.')

    return render(request, 'eray/login.html', {
        'login_form': login_form,
        'next_url': next_url,
    })


def logout(request):
    auth_logout(request)

    return redirect(reverse('home'))


def register(request):
    auth_logout(request)
    register_form = RegistrationForm()

    if request.method == 'POST':
        register_form = RegistrationForm(request.POST, request.FILES)
        if register_form.is_valid():
            register_form.save()
            user = authenticate(
                username=register_form.cleaned_data['username'], password=register_form.cleaned_data['password1'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)

                    return HttpResponseRedirect(reverse('home'))

            return HttpResponseRedirect(reverse('home'))

    return render(request, 'eray/register.html', {
        'register_form': register_form,
    })


@login_required
def post_question(request):
    """Allows creating a new question by a regular user
    """
    post_question_form = PostQuestion()

    if request.method == 'POST':
        post_question_form = PostQuestion(request.POST)

        if post_question_form.is_valid():
            question = post_question_form.save()
            question.user = request.user

            # manually tag the question
            comma_separated_tags = post_question_form.cleaned_data.get('question_tags', '')
            tags = Tag.string_to_objects(comma_separated_tags)

            # manytomany.add takes multiple parameters, but not a list. expand the list into parameters
            question.tags.add(*tags)

            # mark private
            if post_question_form.cleaned_data.get('is_private', False):
                question.status = 'P'

            question.save()

            messages.add_message(request, messages.INFO, 'Question successfully created.')

            return redirect(reverse('question', kwargs={ 'pk': question.pk }))

    return render(request, 'eray/post_question.html', {
        'post_question_form': post_question_form,
    })


@login_required
def tag_autocomplete(request):
    """ AJAX autocomplete data source.
    """
    MAX_RESULTS = 10

    query = request.GET.get('query', '')
    tags_dict = {}

    if query:
        tags = Tag.objects.filter(name__istartswith=query)[:MAX_RESULTS]
        for tag in tags:
            tags_dict[tag.id] = {'id': tag.id,
                                 'name': tag.name
                                 }

    return JsonResponse(tags_dict)


@login_required
def question(request, pk):
    """Individual question page
    """
    question = Question.objects.get(pk=pk)
    post_answer_form = PostAnswer()

    question.track_view(request.user)

    if request.method == 'POST':
        post_answer_form = PostAnswer(request.POST)

        if post_answer_form.is_valid():
            answer = post_answer_form.save()
            answer.user = request.user
            answer.parent = question

            # mark private
            if post_answer_form.cleaned_data.get('is_private', False):
                answer.status = 'P'

            answer.save()

            messages.add_message(request, messages.INFO, 'Answer successfully created.')

            return redirect(reverse('question', kwargs={'pk': question.pk}))

    question_answers =  question.answer_set.all().order_by('-accepted')

    if not request.user.is_superuser:
        question_answers = question_answers.filter(Q(status='A') | Q(user=request.user))

    return render(request, 'eray/question.html', {
        'question': question,
        'question_answers': question_answers,
        'post_answer_form': post_answer_form,
    })


@login_required
def vote_up(request, pk):
    question_pk = pk
    question = False

    if question_pk:
        try:
            question = Question.objects.get(pk=pk)
        except:
            pass

        if question:
            question.vote(request.user, 1)

            return HttpResponse(question.vote_count)

    return HttpResponse('')


@login_required
def vote_down(request, pk):
    question_pk = pk
    question = False

    if question_pk:
        try:
            question = Question.objects.get(pk=pk)
        except:
            pass

        if question:
            question.vote(request.user, -1)

            return HttpResponse(question.vote_count)

    return HttpResponse('')


@login_required
def accept_answer(request, answer_pk):
    answer = get_object_or_404(Answer, pk=answer_pk, user=request.user)
    answer.mark_accepted()

    return HttpResponseRedirect(reverse('question', kwargs={ 'pk': answer.parent.pk }))


@login_required
def vote_up_answer(request, pk):
    answer_pk = pk
    answer = False

    if answer_pk:
        try:
            answer = Answer.objects.get(pk=pk)
        except:
            pass

        if answer:
            answer.vote(request.user, 1)

            return HttpResponse(answer.vote_count)

    return HttpResponse('')


@login_required
def vote_down_answer(request, pk):
    answer_pk = pk
    answer = False

    if answer_pk:
        try:
            answer = Answer.objects.get(pk=pk)
        except:
            pass

        if answer:
            answer.vote(request.user, -1)

            return HttpResponse(answer.vote_count)

    return HttpResponse('')


@login_required
def question_comment(request):
    comment = request.POST.get('body', False)
    user = request.user
    question_pk = request.POST.get('question', False)

    if not question_pk or not comment:

        raise Http404

    if not comment:

        return JsonResponse({'failed': True, 'message': 'Please write a comment.'})

    if len(comment) < 15 or len(comment) > 400:

        return JsonResponse({'failed': True, 'message': 'Please write a comment that has between 15 and 400 characters.'})

    question = get_object_or_404(Question, pk=question_pk)
    question.add_comment(comment, user)

    return JsonResponse({'success': True, 'message': comment})


@login_required
def answer_comment(request):
    comment = request.POST.get('body', False)
    user = request.user
    answer_pk = request.POST.get('answer', False)

    if not answer_pk or not comment:

        raise Http404

    if not comment:

        return JsonResponse({'failed': True, 'message': 'Please write a comment.'})

    if len(comment) < 15 or len(comment) > 400:

        return JsonResponse({'failed': True, 'message': 'Please write a comment that has between 15 and 400 characters.'})

    answer = get_object_or_404(Answer, pk=answer_pk)
    answer.add_comment(comment, user)

    return JsonResponse({'success': True, 'message': comment})


def tag_cloud(request):
    """Community Tag list
    """
    MAX_RESULTS = 100
    page = request.GET.get('page', 1)
    tag_list = Tag.objects.all()

    paginator = ErayPaginator(tag_list, MAX_RESULTS)

    try:
        tags = paginator.page(page)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)

    return render(request, 'eray/tags.html', {
        'tags': tags,
    })

def profile(request, username):
    """User profile page
    """
    user = get_object_or_404(User, username=username)

    return render(request, 'eray/profile.html', {
        'user': user,
    })