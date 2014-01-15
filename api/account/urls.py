from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

import api.account.views as views

urlpatterns = patterns(
    '',
    url('^avatar$', views.avatar, name='api_account_avatar'),
)
