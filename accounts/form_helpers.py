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

USER_UPDATE_FORMS = {
    'update_username_form' : UpdateUsernameForm,
    'update_user_first_name_form' : UpdateUserFirstNameForm,
    'update_user_last_name_form' : UpdateUserLastNameForm,
    'update_user_share_name_form' : UpdateUserShareNameForm,
    'update_user_website_form' : UpdateUserWebsiteForm,
    'update_user_facebook_form' : UpdateUserFacebookForm,
    'update_user_twitter_form' : UpdateUserTwitterForm,
    'update_user_city_form' : UpdateUserCityForm,
    'update_user_state_form' : UpdateUserStateForm,
    'update_user_share_location_form' : UpdateUserShareLocationForm,
    'update_user_biography_form' : UpdateUserBiographyForm,
    }

def get_user_update_form(request):
    update_type = request.POST.get('update_form_type', False)
    update_form = None
    for form_type in USER_UPDATE_FORMS:
        if form_type == update_type:
            update_form = USER_UPDATE_FORMS[form_type]
            break
    return update_form
