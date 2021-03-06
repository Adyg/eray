from __future__ import unicode_literals

import datetime

from slugify import slugify
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Avg, Max, Min, Sum
from django.utils import timezone


class BaseContent(models.Model):
    """
    Abstract model, contains fields common between all content pieces
    """
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('P', 'Private'),
    )

    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    # Denormalized counts
    vote_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def vote(self, user, vote_value=1):
        """Add a vote from a user
        """

        # check if the user already voted
        vote = self.vote_set.filter(basevote__user__pk=user.pk)

        if vote:
            base_votes = vote[0].basevote_set.all()
            for base_vote in base_votes:
                base_vote.value = vote_value
                base_vote.save()
        else:
            vote = Vote.objects.create(**self.get_poly_params())
            base_vote = BaseVote.objects.create(parent=vote, user=user, value=vote_value)

    def get_comments(self):
        """Return the question's comments
        """
        comments = self.comment_set.all()
        base_comments = BaseComment.objects.filter(parent__in=comments)

        return base_comments

    def add_comment(self, body, user):
        """Add a new Comment related to this object
        """
        comment = Comment.objects.create(**self.get_poly_params())
        comment.save()
        base_comment = BaseComment.objects.create(body=body, user=user, parent=comment)
        base_comment.save()

        return comment

    def track_view(self, user):
        """Add a new View related to this object
        """
        # check if the user already viewed the question
        view = self.view_set.filter(baseview__user__pk=user.pk)

        if not view:
            view = View.objects.create(**self.get_poly_params())
            view.save()
            base_view = BaseView.objects.create(parent=view, user=user)
            base_view.save()            

    def get_poly_params(self):
        """Return a dictionary populated with either a question or an answer element,
        depending on the type of the child inheriting from this abstract class
        """
        object_type = self.__class__.__name__

        if object_type == 'Question':
            return { 'question': self }

        return { 'answer': self }

    def get_link(self):
        domain = Site.objects.get_current().domain
        path = ''

        if type(self) is Question:
            path = reverse('question', kwargs={'slug': self.slug})
        elif type(self) is Comment:
            path = reverse('question', kwargs={'slug': self.parent.slug})

        url = '//{domain}{path}'.format(domain=domain, path=path)

        return url


class AllTagManager(models.Manager):
    """
    Tag manager that retrieves all Tags, including Inactive ones
    """

    def get_query_set(self):
        return super(AllTagManager, self).get_query_set()


class TagManager(models.Manager):
    """
    Default Tag manager that only retrieves Active Tags
    """

    def get_query_set(self):
        return super(TagManager, self).get_query_set().filter(status='A')


class Tag(models.Model):
    """
    Tags will be used for filtering questions.
    """
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )

    name = models.CharField(max_length=80)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    description = models.TextField(max_length=300, blank=True, null=True)

    # default filtering will only be applied to active tags. Inactive tags
    # have to be explicitly asked for by using Tag.all_objects
    objects = TagManager()
    all_objects = AllTagManager()

    def __unicode__(self):

        return self.name

    @classmethod
    def string_to_objects(cls, comma_separated_tags):
        """
        Splits a comma separated string into words and retrieves the tag objects
        """
        tag_names = [v.strip() for v in comma_separated_tags.split(',')]

        return cls.objects.filter(name__in=tag_names)


class AllQuestionManager(models.Manager):
    """
    Question manager that retrieves all Questions, including Inactive and Private ones
    """

    def get_query_set(self):
        return super(AllQuestionManager, self).get_query_set()


class PrivateQuestionManager(models.Manager):
    """
    Question manager that retrieves only private Questions
    """

    def get_query_set(self):
        return super(PrivateQuestionManager, self).get_query_set().filter(status='P')


class QuestionManager(models.Manager):
    """
    Default Question manager that only retrieves Active and NOT Private ones
    """

    def get_query_set(self):
        return super(QuestionManager, self).get_query_set().filter(status='A')


class Question(BaseContent):
    """
    Questions model
    """
    tags = models.ManyToManyField(Tag, related_name="questions")
    title = models.CharField(max_length=140, unique=True)
    slug = models.CharField(db_index=True, max_length=140, blank=True, null=True)

    # default filtering will only be applied to active questions.
    # inactive and private questions have to be explicitly asked for by using Question.all_objects
    objects = QuestionManager()
    all_objects = AllQuestionManager()
    private_objects = PrivateQuestionManager()

    def __unicode__(self):

        return self.title

    def answer_count(self):
        """Return the question's answer count
        """
        return self.answer_set.all().count()

    def related_questions(self):

        return Question.objects.all().order_by('?')[:4]

    def related_tag_questions(self):
        tags = self.tags.all()

        questions = Question.objects.filter(tags__in=tags)[:4]

        return questions

    def latest_answered_questions(self):
        answers = Answer.objects.all().order_by('-created_at')[:4]

        questions = []

        for answer in answers:
            questions.append(answer.parent)

        return questions

    def save(self, *args, **kwargs):
        """Override save() to set the question slug
        """
        self.slug = slugify(self.title)

        super(Question, self).save(*args, **kwargs)



class AllAnswerManager(models.Manager):
    """
    Answer manager that retrieves all Answers
    """

    def get_query_set(self):
        return super(AllAnswerManager, self).get_query_set()


class AnswerManager(models.Manager):
    """
    Default Answer manager that only retrieves Active ones
    """

    def get_query_set(self):
        return super(AnswerManager, self).get_query_set().filter(status='A')


class Answer(BaseContent):
    """
    Answer model
    """
    parent = models.ForeignKey(Question, blank=True, null=True)
    accepted = models.BooleanField(default=False)

    # default filtering will only be applied to active answers.
    # inactive answers have to be explicitly asked for by using Answer.all_objects
    objects = AnswerManager()
    all_objects = AllAnswerManager()


    def mark_accepted(self):
        """Mark the answer as accepted. Ensures only 1 accepted answer per question
        """
        # only 1 accepted answer per question
        Answer.objects.filter(parent=self.parent).update(accepted=False)

        self.accepted = True
        self.save()


class Comment(models.Model):
    """
    Intermediate model that relates a BaseComment to either a Question or an Answer
    """
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)


class AllCommentManager(models.Manager):
    """
    Comment manager that retrieves all Comments
    """

    def get_query_set(self):
        return super(AllCommentManager, self).get_query_set()


class CommentManager(models.Manager):
    """
    Default Comment manager that only retrieves Active ones
    """

    def get_query_set(self):
        return super(CommentManager, self).get_query_set().filter(status='A')


class BaseComment(models.Model):
    """
    Comment base model. Comments are replies to either Question or Answer.
    BaseComment is related to either a Question or Answer through Comment
    """
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )

    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey(Comment, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    user = models.ForeignKey(User)

    # default filtering will only be applied to active comments.
    # inactive comments have to be explicitly asked for by using Comment.all_objects
    objects = CommentManager()
    all_objects = AllCommentManager()


class Vote(models.Model):
    """
    Intermediate model that relates a BaseVote to either a Question or an Answer
    """
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)

    def get_parent_obj(self):
        """Returns a Question or an Answer
        """
        if self.question:

            return self.question

        return self.answer


class BaseVote(models.Model):
    """
    Vote base model. Votes can be related to either a Question or an Answer.
    BaseVote is related to either a Question or an Answer through Vote
    """
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey(Vote)
    user = models.ForeignKey(User)
    value = models.IntegerField(default=0)


class View(models.Model):
    """
    Intermediate model that relates a BaseView to either a Question or an Answer
    """
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)


class BaseView(models.Model):
    """
    View base model. Views can be related to either a Question or an Answer.
    BaseView is related to either a Question or an Answer through Vote
    """
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey(View)
    user = models.ForeignKey(User)
    value = models.IntegerField(default=1)

    