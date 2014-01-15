from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

import api.users.views as views

urlpatterns = patterns(
    '',
    url('^suggest$', views.suggest, name='api_users_suggest'),
)
