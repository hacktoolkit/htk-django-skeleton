import datetime

from django.conf import settings
from django.core.urlresolvers import reverse

from htk.apps.feedback.forms import FeedbackForm

from hacktoolkit.constants import *
from htk.view_helpers import get_asset_version
from htk.utils import utcnow

def wrap_data(request, data=None):
    if data is None:
        data = {}

    ##
    # meta
    path = request.path
    host = request.get_host()
    is_secure = request.is_secure()
    full_uri = '%s://%s%s' % ('http' + ('s' if is_secure else ''), host, path,)
    data['is_secure'] = is_secure
    data['host'] = host
    data['path'] = path
    data['full_uri'] = full_uri
    data['server_hostname'] = settings.SERVER_HOSTNAME
    data['rollbar_env'] = settings.ROLLBAR_ENV
    # LESS http://lesscss.org/#usage
    useless = settings.ENV_DEV and request.GET.get('useless', False)
    data['css_rel'] = 'stylesheet/less' if useless else 'stylesheet'
    data['css_ext'] = 'less' if useless else 'css?v=%s' % get_asset_version()

    ##
    # user
    if request.user.is_authenticated():
        user = request.user
        feedback_form_initial = {
            'user' : user,
            'name' : user.profile.get_display_name,
            'email' : user.email,
        }
        feedback_form = FeedbackForm(initial=feedback_form_initial)
    else:
        user = None
        feedback_form = FeedbackForm(None)
        # TODO: fix this query string next thing
        data['query_string'] = request.META.get('QUERY_STRING')

    data['user'] = user
    data['feedback_form'] = feedback_form

    ##
    # header
    nav_links = [
    ]
    data['nav_links'] = nav_links

    ##
    # conditional header
    # minimal distractions on registration and login page
    # don't display multiple logos on one page

    hide_logo_views = [
        reverse('htk_prelaunch'),
        reverse('home'),
        reverse('account_login'),
        reverse('account_register'),
    ]

    hide_header_views = [
        reverse('htk_prelaunch'),
        reverse('home'),
        reverse('account_login'),
        reverse('account_register'),
        reverse('account_register_social_email'),
        reverse('account_register_social_login'),
    ]

    hide_login_register_views = [
        reverse('htk_prelaunch'),
        reverse('account_login'),
        reverse('account_register'),
        reverse('account_register_social_email'),
        reverse('account_register_social_login'),
    ]

    if path not in hide_logo_views:
        data['show_header_logo'] = True
 
    if path not in hide_header_views:
        data['show_header_nav'] = True

    if path not in hide_login_register_views:
        data['show_login_register'] = True

    ##
    # errors
    data['errors'] = []

    ##
    # footer
    if path == reverse('htk_prelaunch'):
        footer_links = []
    else:
        footer_links = [
            { 'text': 'Home', 'uri': reverse('home'), 'selected': path == reverse('home') },
            { 'text': 'About', 'uri': reverse('about'), 'selected': path == reverse('about') },
            { 'text': 'Help', 'uri': reverse('help'), 'selected': path == reverse('help') },
            { 'text': 'Terms of Service', 'uri': reverse('tos'), 'selected': path == reverse('tos') },
            { 'text': 'Privacy Policy', 'uri': reverse('privacy'), 'selected': path == reverse('privacy') },
        ]

    data['footer_links'] = footer_links

    current_year = datetime.date.today().year
    if FOUNDING_YEAR < current_year:
        data['copyright_years'] = '%d - %d' % (FOUNDING_YEAR, current_year,)
    else:
        data['copyright_years'] = current_year

    return data
