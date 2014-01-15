from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

import api.views as views

urlpatterns = patterns(
    '',
    # subdirectories
    url('^account/', include('api.account.urls')),
    url('^users/', include('api.users.urls')),
)
