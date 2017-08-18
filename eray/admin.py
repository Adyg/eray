from django.contrib import admin

from eray.models.content import (Question, Tag, Vote, BaseVote, Answer, Comment, BaseComment, View, BaseView, )
from eray.models.achievements import (Achievement, )
from eray.models.user import (Profile)

admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Vote)
admin.site.register(BaseVote)
admin.site.register(Answer)
admin.site.register(Comment)
admin.site.register(BaseComment)
admin.site.register(View)
admin.site.register(BaseView)
admin.site.register(Profile)
admin.site.register(Achievement)