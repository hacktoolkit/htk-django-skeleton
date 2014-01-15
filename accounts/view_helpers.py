from django.shortcuts import redirect

from accounts.constants import *
from accounts.forms import UpdateUserBiographyForm
from accounts.forms import UpdateUserCityForm
from accounts.forms import UpdateUserFacebookForm
from accounts.forms import UpdateUserFirstNameForm
from accounts.forms import UpdateUserLastNameForm
from accounts.forms import UpdateUserShareLocationForm
from accounts.forms import UpdateUserShareNameForm
from accounts.forms import UpdateUserStateForm
from accounts.forms import UpdateUserTwitterForm
from accounts.forms import UpdateUserWebsiteForm
from accounts.forms import UpdateUsernameForm
from accounts.session_keys import *

from hacktoolkit.view_helpers import wrap_data

def wrap_data_accounts(request, data = None):
    if data == None:
        data = {}
    data = wrap_data(request, data)

    # logged in
    user = data.get('user', None)
    if user:
        pass
    else:
        pass
    return data

def get_social_auths_status(user):
    user_social_auths = user.profile.get_social_auths()
    status_dict = {}
    for social_auth in user_social_auths:
        #status_dict[social_auth.provider] = social_auth.id
        status_dict[social_auth.provider] = True

    status_list = []
    for social_auth in SOCIAL_AUTHS:
        key = social_auth['key']
        name = social_auth['name']
        item = {
            'key' : key,
            'name' : name,
            #'id' : status_dict.get(key, None),
            'linked' : status_dict.get(key, False),
        }
        status_list.append(item)
    return status_list

def redirect_to_social_auth_complete(request):
    """Return an HTTP Redirect response to social:complete to continue the pipeline
    """
    backend = request.session[SOCIAL_AUTH_PARTIAL_PIPELINE_KEY]['backend']
    response = redirect('social:complete', backend=backend)
    return response

def get_social_auths_status(user):
    user_social_auths = user.profile.get_social_auths()
    status_dict = {}
    for social_auth in user_social_auths:
        status_dict[social_auth.provider] = True

    status_list = []
    for social_auth in SOCIAL_AUTHS:
        key = social_auth['key']
        name = social_auth['name']
        item = {
            'key' : key,
            'name' : name,
            'linked' : status_dict.get(key, False)
        }
        status_list.append(item)
    return status_list

def get_user_update_forms(user):
    user_update_forms = [
        {
            'key' : 'update_username_form',
            'form' : UpdateUsernameForm(user, initial = {'username' : user.username if user.profile.has_username_set else '' }),
        },
        {
            'key' : 'update_user_first_name_form',
            'form' : UpdateUserFirstNameForm(user, instance=user),
        },
        {
            'key' : 'update_user_last_name_form',
            'form' : UpdateUserLastNameForm(user, instance=user),
        },
        {
            'key' : 'update_user_share_name_form',
            'form' : UpdateUserShareNameForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_website_form',
            'form' : UpdateUserWebsiteForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_facebook_form',
            'form' : UpdateUserFacebookForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_twitter_form',
            'form' : UpdateUserTwitterForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_city_form',
            'form' : UpdateUserCityForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_state_form',
            'form' : UpdateUserStateForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_share_location_form',
            'form' : UpdateUserShareLocationForm(user, instance=user.profile),
        },
        {
            'key' : 'update_user_biography_form',
            'form' : UpdateUserBiographyForm(user, instance=user.profile),
        },
    ]
    return user_update_forms
