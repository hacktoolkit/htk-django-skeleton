from hashlib import sha1
import datetime
import random

from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36

from hacktoolkit.constants import *
from htk.mailers import send_email

def activation_email(user_email, use_https=False, domain=DEFAULT_EMAIL_SENDING_DOMAIN):
    """Sends an activation/confirmation email for user to confirm email address
    """
    user = user_email.user
    email = user_email.email

    context = {
        'user': user,
        'email': email,
        'protocol': use_https and 'https' or 'http', 
        'domain': domain,
        'confirm_email_path': reverse('account_confirm_email', args=(user_email.activation_key,)),
    }

    activation_uri = '%(protocol)s://%(domain)s%(confirm_email_path)s' % context
    context['activation_uri'] = activation_uri
    send_email(
        template='accounts/activation',
        subject='Confirm your email address, %s' % email,
        to=[email],
        context=context,
        bcc=[WATCHER_EMAIL]
    )

def welcome_email(user):
    context = {
        'user': user,
    }
    send_email(
        template='accounts/welcome',
        subject='Welcome to Hacktoolkit.com, %s' % user.email,
        to=[user.email],
        context=context,
        bcc=[WATCHER_EMAIL]
    )

def password_reset_email(user, token_generator, use_https=False, domain=DEFAULT_DOMAIN):
    context = {
        'user': user,
        'email': user.email,
        'protocol': use_https and 'https' or 'http', 
        'domain': domain,
        'site_name': 'Hacktoolkit',
        'reset_path': reverse('account_reset_password'),
        'uid': int_to_base36(user.id),
        'token': token_generator.make_token(user),
    }

    reset_uri = '%(protocol)s://%(domain)s%(reset_path)s?u=%(uid)s&t=%(token)s' % context
    context['reset_uri'] = reset_uri
    send_email(
        template='accounts/reset_password',
        subject='Password reset on %s' % context['site_name'],
        to=[context['email']],
        context=context
    )
