import datetime
from haystack import indexes
from eray.models.content import Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='body', null=True, use_template=True)
    created_at = indexes.DateTimeField(model_attr='created_at')
    title = indexes.CharField(model_attr='title')
    tags = indexes.MultiValueField()
    slug = indexes.CharField(model_attr='slug')
    spelling_suggestions = indexes.FacetCharField()

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_tags(self, obj):
        if obj.tags:
            return ['{}'.format(tag.name) for tag in obj.tags.all()]

        return []