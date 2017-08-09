from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,)

from eray.models.content import (Question, Tag, Answer)
from eray.utils import pluralize


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'

        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class RegistrationForm(UserCreationForm):
    """Registration form
    """
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')        

    def save(self,commit = True):   
        user = super(RegistrationForm, self).save()

        return user


class PostQuestion(forms.ModelForm):
    """
    Form that handles creating questions for the regular users
    """
    # the Tag autocomplete input. It will populate the Question.tags field
    question_tags = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PostQuestion, self).__init__(*args, **kwargs)

        # ensure the title is not longer than the length the field allows
        self.fields['title'] = forms.CharField(max_length=Question._meta.get_field('title').max_length)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['placeholder'] = 'What\'s your question?'

        self.fields['question_tags'].widget.attrs['class'] = 'form-control'
        self.fields['question_tags'].widget.attrs[
            'placeholder'] = 'Provide at least one tag for your question, separate tags by comma'

    def clean_question_tags(self):
        """
        Ensure the user only uses approved tags or has the permission to create new ones
        """
        cleaned_data = super(PostQuestion, self).clean()
        raw_question_tags = cleaned_data.get('question_tags')

        # split the comma separated tag list into tag names and get rid of any leading or trailing whitespaces
        question_tags = [v.strip() for v in raw_question_tags.split(',')]

        # check if there are any inexistent tags
        approved_tags = Tag.string_to_objects(raw_question_tags)

        # list of approved tags doesn't have the same number of elements as the one the user inputed, something is wrong
        if approved_tags.count() != len(question_tags):
            approved_tags_name = approved_tags.values_list('name', flat=True)

            # get the tags that are not approved
            unapproved_tags = list(set(question_tags) - set(approved_tags_name))
            unaproved_tags_count = len(unapproved_tags)

            self._errors['question_tags'] = 'The {} {} {} not valid. Please use existing tags or ask for them to be added by an admin.'.format(
                ', '.join(unapproved_tags), pluralize(unaproved_tags_count, 'tag', 'tags'), pluralize(unaproved_tags_count, 'is', 'are'))

        return raw_question_tags

    class Meta:
        model = Question
        fields = ['title', 'body', ]


class PostAnswer(forms.ModelForm):
    """
    Form that handles creating answers for the regular users
    """

    # the Is Private checkbox. If checked, it should set the Question.status field to Private
    is_private = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(PostAnswer, self).__init__(*args, **kwargs)

    class Meta:
        model = Answer
        fields = ['body', ]
