from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Avg, Max, Min, Sum, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from eray.forms import PostQuestion, PostAnswer, LoginForm
from eray.models import (Tag, Question, Answer,)


def homepage(request):

    return render(request, 'eray/homepage.html', {
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


def documentation(request):

    return render(request, 'eray/documentation.html', {})


@csrf_exempt
def community(request):

    return render(request, 'eray/community.html', {})


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

            return redirect(reverse('community'))

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
def community(request):
    """Community question list
    """
    MAX_RESULTS = 10
    page = request.GET.get('page', 1)
    order = request.GET.get('order', False)

    if request.user.is_superuser:
        question_list = Question.all_objects.all()
    else:
        question_list = Question.all_objects.filter(Q(status='A') | Q(user=request.user))

    if order:
        if order == 'date':
            question_list = question_list.order_by('-created_at')

        # Coalesce will be used below to avoid NULL values interfering with the ordering
        # Track https://code.djangoproject.com/ticket/10929 for future alternatives
        if order == 'votes':
            question_list = question_list.annotate(total_votes=Coalesce(
                Sum('vote__basevote__value'), 0)).order_by('-total_votes')

        if order == 'views':
            question_list = question_list.annotate(total_views=Coalesce(
                Sum('view__baseview__value'), 0)).order_by('-total_views')

        if order == 'answers':
            question_list = question_list.annotate(total_answers=Coalesce(Sum('answer'), 0)).order_by('-total_answers')

    paginator = Paginator(question_list, 10)

    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    return render(request, 'eray/community.html', {
        'questions': questions,
        'date_format': settings.DATE_FORMAT,
        'order': order,
    })


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

    if request.user.is_superuser:
        question_answers = question.answer_set.all()
    else:
        question_answers = question.answer_set.filter(Q(status='A') | Q(user=request.user))

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

            return HttpResponse(question.votes_count())

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

            return HttpResponse(question.votes_count())

    return HttpResponse('')


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

            return HttpResponse(answer.votes_count())

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

            return HttpResponse(answer.votes_count())

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
