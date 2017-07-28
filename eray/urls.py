from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

from eray import views as eray_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'minicalorie.views.home', name='home'),
    # url(r'^minicalorie/', include('minicalorie.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # placeholders
    url(r'^$', eray_views.homepage, name='home'),

    # auth
    url(r'^accounts/login/$', eray_views.login, name='login'),
    url(r'^logout/$', eray_views.logout, name='logout'),
    url(r'^accounts/create/$', eray_views.register, name='register'),

    # post question
    url(r'^ask/$', eray_views.post_question, name='question'),

    # tag autocomplete, called via AJAX
    url(r'^tag-autocomplete/$', eray_views.tag_autocomplete, name='tag-autocomplete'),

    # question detail page
    url(r'^question/(?P<pk>\d+)/$', eray_views.question, name='question'),

    # vote up question
    url(r'^vote/up/question/(?P<pk>\d+)/$', eray_views.vote_up, name='vote-up'),    

    # vote down question
    url(r'^vote/down/question/(?P<pk>\d+)/$', eray_views.vote_down, name='vote-down'),    

    # vote up answer
    url(r'^vote/up/answer/(?P<pk>\d+)/$', eray_views.vote_up_answer, name='vote-up-answer'),    

    # vote down answer
    url(r'^vote/down/answer/(?P<pk>\d+)/$', eray_views.vote_down_answer, name='vote-down-answer'),

    # question comment
    url(r'^question/comment/$', eray_views.question_comment, name='question-comment'),     

    # answer comment
    url(r'^answer/comment/$', eray_views.answer_comment, name='answer-comment'),     
]

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

