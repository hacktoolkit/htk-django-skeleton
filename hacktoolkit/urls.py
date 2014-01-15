from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from django.contrib import admin

admin.autodiscover()

from hacktoolkit.sitemaps import SITEMAPS
import hacktoolkit.views as views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^home$', views.home, name='home'),
    url(r'^about$', views.about, name='about'),
    url(r'^help$', views.help, name='help'),
    url(r'^tos$', views.tos, name='tos'),
    url(r'^privacy$', views.privacy, name='privacy'),
    # apps
    url(r'^account/', include('accounts.urls')),
    url(r'^api/', include('api.urls')),
    # admin
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^htkadmin/', include('hacktoolkit.htkadmin.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # django-social-auth
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    # htk
    url(r'', include('htk.urls')),
    url(r'^feedback/', include('htk.apps.feedback.urls')),
    url(r'^prelaunch/', include('htk.apps.prelaunch.urls')),
    # meta
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', { 'sitemaps': SITEMAPS }, name='sitemap'),
)

if settings.ENV_DEV:
    urlpatterns += patterns(
        '', 
        url(r'^500$', views.error500, name='error500'),
        url(r'^404$', views.error404, name='error404'),
    )
