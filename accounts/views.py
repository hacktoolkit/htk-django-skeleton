import datetime

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_reset
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.http import base36_to_int
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET

from accounts.constants import *
from accounts.decorators import logged_in_redirect_home
from accounts.decorators import logout_required
from accounts.form_helpers import get_user_update_form
from accounts.forms import AddEmailForm
from accounts.forms import PasswordResetFormHtmlEmail
from accounts.forms import ResendConfirmationForm
from accounts.forms import SocialRegistrationAuthenticationForm
from accounts.forms import SocialRegistrationEmailForm
from accounts.forms import TimezoneForm
from accounts.forms import UserRegistrationForm
from accounts.forms import UsernameEmailAuthenticationForm
from accounts.models import UserEmail
from accounts.models import UserProfile
from accounts.session_keys import *
from accounts.utils import get_user_by_email
from accounts.utils import get_user_email
from accounts.view_helpers import get_social_auths_status
from accounts.view_helpers import get_user_update_forms
from accounts.view_helpers import redirect_to_social_auth_complete
from accounts.view_helpers import wrap_data_accounts

from htk.api.utils import json_response
from htk.api.utils import json_response_error
from htk.api.utils import json_response_okay

from htk.utils import utcnow
from htk.view_helpers import render_to_response_custom as _r

@login_required
def index(request):
    response = redirect('account_home')
    return response

@login_required
def home(request):
    response = redirect('account_settings')
    return response

@login_required
def settings(request):
    data = wrap_data_accounts(request)
    data.update(csrf(request))    
    user = data['user']

    data['social_auths_status'] = get_social_auths_status(user)
    data['user_update_forms'] = get_user_update_forms(user)

    if request.method == 'POST':
        user_update_form_class = get_user_update_form(request)
        user_update_form = user_update_form_class(user, request.POST)
        if user_update_form.is_valid():
            success = True
            result = user_update_form.save()
            response = json_response_okay()
        else:
            response = json_response_error()
    else:
        response = _r('account/settings.html', data)
    return response

@login_required
def emails(request):
    data = wrap_data_accounts(request)
    user = data['user']
    data.update(csrf(request))

    add_email_form = None
    success = False
    if request.method == 'POST':
        if 'add_email' in request.POST:
            add_email_form = AddEmailForm(request.POST)
            if add_email_form.is_valid():
                domain = request.get_host()
                user_email = add_email_form.save(user=user, domain=domain)
                success = True
            else:
                for error in add_email_form.non_field_errors():
                    data['errors'].append(error)
        elif 'primary_email' in request.POST:
            email = request.POST.get('primary_email')
            user_email = get_object_or_404(UserEmail, user=user, email=email)
            user = user_email.set_primary_email()
            if user:
                # update cached user object
                data['user'] = user
                success = True
        elif 'delete_email' in request.POST:
            email = request.POST.get('delete_email')
            user_email = get_object_or_404(UserEmail, user=user, email=email)
            if user_email.delete():
                success = True
        else:
            # unknown POST
            raise Http404
    else:
        # just render the page if it is not a post
        pass

    # will need to display AddEmailForm regardless of result
    # reset the form to allow adding another email
    if not add_email_form:
        add_email_form = AddEmailForm()
    data['add_email_form'] = add_email_form

    response = _r('account/emails.html', data)
    return response

@login_required
def password(request):
    data = wrap_data_accounts(request)
    user = data['user']
    data.update(csrf(request))

    success = False
    if request.method == 'POST':
        password_form = SetPasswordForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            success = True
    else:
        password_form = SetPasswordForm(None)
    data['password_form'] = password_form

    if success:
        response = redirect(reverse('account_settings'))
    else:
        response = _r('account/password.html', data)
    return response

@login_required
def timezone(request):
    data = wrap_data_accounts(request)
    user = data['user']
    data.update(csrf(request))

    success = False
    if request.method == 'POST':
        timezone_form = TimezoneForm(request.POST)
        if timezone_form.is_valid():
            timezone = timezone_form.save(user, request)
            success = True
        else:
            for error in timezone_form.non_field_errors():
                data['errors'].append(error)
    else:
        timezone_form = TimezoneForm(instance=user.profile)

    if success:
        response = redirect('account_settings')
    else:
        data['timezone_form'] = timezone_form
        response = _r('account/timezone.html', data)
    return response

########################################################################
# login and logout

@logout_required
def logout_view(request):
    logout(request)
    return redirect('home')

@logged_in_redirect_home
def login_view(request):
    data = wrap_data_accounts(request)
    data.update(csrf(request))
    next_view = None
    success = False
    if request.method == 'POST':
        auth_form = UsernameEmailAuthenticationForm(None, request.POST)
        if auth_form.is_valid():
            user = auth_form.get_user()
            login(request, user)
            success = True
            user.profile.update_locale_info_by_ip_from_request(request)
            next_view = request.GET.get('next', reverse('account_home'))
        else:
            for error in auth_form.non_field_errors():
                data['errors'].append(error)
            auth_user = auth_form.get_user()
            if auth_user and not auth_user.is_active:
                data['errors'].append('Have you confirmed your email address yet? <a href="%s">Resend confirmation</a>.' % reverse('account_resend_confirmation'))
    else:
        auth_form = UsernameEmailAuthenticationForm(None)
    if success:
        response = redirect(next_view)
    else:
        data['next'] = next_view
        data['auth_form'] = auth_form
        response = _r('account/login.html', data)
    return response

########################################################################
# registration and activation

@logged_in_redirect_home
def register_social_email(request):
    data = wrap_data_accounts(request)
    data.update(csrf(request))
    email = None
    success = False
    if request.method == 'POST':
        email_form = SocialRegistrationEmailForm(request.POST)
        if email_form.is_valid():
            email = email_form.save(request)
            success = True
        else:
            for error in email_form.non_field_errors():
                data['errors'].append(error)
    else:
        email_form = SocialRegistrationEmailForm(None)

    if success:
        user = get_user_by_email(email)
        if user:
            # a user is already associated with this email
            response = redirect('account_register_social_login')
        else:
            response = redirect_to_social_auth_complete(request)
    else:
        data['email_form'] = email_form
        response = _r('account/register_social_email.html', data)
    return response

@logged_in_redirect_home
def register_social_login(request):
    data = wrap_data_accounts(request)
    email = request.session.get(SOCIAL_REGISTRATION_SETTING_EMAIL)
    data['email'] = email
    data.update(csrf(request))
    success = False
    if request.method == 'POST':
        auth_form = SocialRegistrationAuthenticationForm(email, request.POST)
        if auth_form.is_valid():
            user = auth_form.get_user()
            login(request, user)
            success = True
        else:
            for error in auth_form.non_field_errors():
                data['errors'].append(error)
            auth_user = auth_form.get_user()
            if auth_user and not auth_user.is_active:
                data['errors'].append('Have you confirmed your email address yet? <a href="%s">Resend confirmation</a>.' % reverse('account_resend_confirmation'))
    else:
        auth_form = SocialRegistrationAuthenticationForm(email)

    if success:
        response = redirect_to_social_auth_complete(request)
    else:
        data['auth_form'] = auth_form
        response = _r('account/register_social_login.html', data)
    return response

@logged_in_redirect_home
def register(request):
    data = wrap_data_accounts(request)
    data.update(csrf(request))
    success = False
    if request.method == 'POST':
        reg_form = UserRegistrationForm(request.POST)
        if reg_form.is_valid():
            domain = request.get_host()
            new_user = reg_form.save(domain)
            #username = user.username
            #password = reg_form.cleaned_data.get('password1') # user.password is a hashed value
            #auth_user = authenticate(username=username, password=password)
            #login(request, auth_user)
            success = True
        else:
            for error in reg_form.non_field_errors():
                data['errors'].append(error)
    else:
        reg_form = UserRegistrationForm()
    data['reg_form'] = reg_form
    destination = None
    if success:
        destination = redirect(reverse('account_register_done'))
    else:
        destination = _r('account/register.html', data)
    return destination

def register_done(request):
    data = wrap_data_accounts(request)
    response = _r('account/register_done.html', data)
    return response

@logged_in_redirect_home
def resend_confirmation(request):
    data = wrap_data_accounts(request)
    data.update(csrf(request))
    if request.method == 'POST':
        resend_confirmation_form = ResendConfirmationForm(request.POST)
        if resend_confirmation_form.is_valid():
            email = resend_confirmation_form.cleaned_data.get('email')
            user_emails = UserEmail.objects.filter(email=email)
            num_confirmed_user_emails = user_emails.filter(is_confirmed=True).count()
            if num_confirmed_user_emails == 1:
                data['already_active'] = True
            elif num_confirmed_user_emails > 1:
                raise NonUniqueEmail(email)
            else:
                unconfirmed_user_emails = user_emails.filter(is_confirmed=False)
                for unconfirmed in unconfirmed_user_emails:
                    unconfirmed.send_activation_email(domain=request.get_host(), resend=True)
                data['success'] = True
        else:
            for error in resend_confirmation_form.non_field_errors():
                data['errors'].append(error)
    else:
        resend_confirmation_form = ResendConfirmationForm()
    data['resend_confirmation_form'] = resend_confirmation_form
    response = _r('account/resend_confirmation.html', data)
    return response

@require_GET
def confirm_email(request, activation_key):
    data = wrap_data_accounts(request)
    user = data['user']
    user_email = get_object_or_404(UserEmail,
                                   activation_key=activation_key)
    if user and user != user_email.user:
        # for a mismatched user, force logout
        logout(request)
        user = None
        data['user'] = None

    # attempt to confirm
    if user_email.key_expires < utcnow():
        data['expired'] = True
    else:
        was_activated = user_email.confirm_and_activate_account()
        data['was_activated'] = was_activated
        data['success'] = True

    response = _r('account/confirm_email.html', data)

    return response

########################################################################
# password reset

@logged_in_redirect_home
def forgot_password(request):
    data = wrap_data_accounts(request)
    response = password_reset(
        request,
        template_name='account/forgot_password.html',
        password_reset_form=PasswordResetFormHtmlEmail,
        post_reset_redirect=reverse('account_password_reset_done'),
        extra_context = data
    )
    return response

def password_reset_done(request):
    data = wrap_data_accounts(request)
    response = _r('account/password_reset_done.html', data)
    return response

# Doesn't need csrf_protect since no one can guess the URL
@csrf_exempt
@logout_required
def reset_password(request):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.

    Based off of django.contrib.auth.views.password_reset_confirm
    Need to customize error display
    """
    data = wrap_data_accounts(request)
    uidb36 = request.GET.get('u', None)
    token = request.GET.get('t', None)
    token_generator = default_token_generator
    success = False
    destination = None
    if uidb36 and token:
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            user = None

        if user is not None and token_generator.check_token(user, token):
            validlink = True
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    success = True
            else:
                form = SetPasswordForm(None)
        else:
            validlink = False
            form = None
        data['form'] = form
        data['validlink'] = validlink
    else:
        data['validlink'] = False
    if success:
        destination = redirect(reverse('account_password_reset_success'))
    else:
        if not data['validlink']:
            data['errors'].append('Invalid Link.')
            data['forgot_password_link'] = reverse('account_forgot_password')
        destination = _r('account/reset_password.html', data)
    return destination

def password_reset_success(request):
    data = wrap_data_accounts(request)
    response = _r('account/password_reset_success.html', data)
    return response
