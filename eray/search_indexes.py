import datetime
from haystack import indexes
from eray.models import Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='body', null=True)
    created_at = indexes.DateTimeField(model_attr='created_at')
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
