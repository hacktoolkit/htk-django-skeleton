from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

import accounts.views as views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='account_index'),
    url(r'^home$', views.home, name='account_home'),
    url(r'^settings$', views.settings, name='account_settings'),
    url(r'^emails$', views.emails, name='account_emails'),
    url(r'^password$', views.password, name='account_password'),
    url(r'^timezone$', views.timezone, name='account_timezone'),
    # account management
    url(r'^login$', views.login_view, name='account_login'),
    #url(r'^login_error$', views.login_error, name='account_login_error'),
    url(r'^logout$', views.logout_view, name='account_logout'),
    # account registration and activation
    url(r'^register_social_email$', views.register_social_email, name='account_register_social_email'),
    url(r'^register_social_login$', views.register_social_login, name='account_register_social_login'),
    url(r'^register$', views.register, name='account_register'),
    url(r'^register_done$', views.register_done, name='account_register_done'),
    url(r'^resend_confirmation$', views.resend_confirmation, name='account_resend_confirmation'),
    url(r'^confirm_email/([a-z0-9]+)$', views.confirm_email, name='account_confirm_email'),
    # password reset
    url(r'^forgot_password$', views.forgot_password, name='account_forgot_password'),
    url(r'^password_reset_done', views.password_reset_done, name='account_password_reset_done'),
    url(r'^reset_password$', views.reset_password, name='account_reset_password'),
    url(r'^password_reset_success', views.password_reset_success, name='account_password_reset_success'),
)
