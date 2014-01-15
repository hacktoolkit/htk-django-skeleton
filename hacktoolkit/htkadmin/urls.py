from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

import hacktoolkit.htkadmin.views as views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='htkadmin'),
#    url(r'^pulse$', views.pulse, name='htkadmin_pulse'),
)
