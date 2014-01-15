import base64
import hashlib

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import email_re

from accounts.constants import *
from accounts.exceptions import NonUniqueEmail
from accounts.models import UserEmail

from hacktoolkit.constants import *

def email_to_username_hash(email):
    """Convert emails to hashed versions where we store them in the username field
    We can't just store them directly, or we'd be limited to Django's username <= 30 chars limit,
    which is really too small for arbitrary emails

    From: https://github.com/dabapps/django-email-as-username/blob/master/emailusernames/utils.py
    """
    # Emails should be case-insensitive unique
    email = email.lower()
    # Deal with internationalized email addresses
    converted = email.encode('utf8', 'ignore')
    return base64.urlsafe_b64encode(hashlib.sha256(converted).digest())[:EMAIL_TO_USERNAME_HASH_LENGTH]

def get_user_by_username(username):
    """Gets a user by `username`
    Returns None if not found
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user

def get_user_by_email(email, auth=False):
    """Gets a User by `email`
    Returns None if not found
    """
    if email_re.search(email):
        # check for confirmed email addresses
        user_emails = UserEmail.objects.filter(email=email, is_confirmed=True)
        num_results = user_emails.count()
        if num_results == 1:
            user = user_emails[0].user
        elif num_results > 1:
            # there should only be one User with this email...
            # if there are more, we have a data error!
            raise NonUniqueEmail(email)
        elif not auth:
            # num_results == 0
            # also check newly registered accounts if not performing authentication
            user = get_incomplete_signup_user_by_email(email)
        else:
            # nope
            user = None
    else:
        user = None
    return user

def get_incomplete_signup_user_by_email(email):
    """Gets an incomplete signup User by `email`
    Returns None if not found
    """
    user_emails = UserEmail.objects.filter(email=email, is_confirmed=False)
    num_results = user_emails.count()
    user = None
    if num_results == 1:
        user = user_emails[0].user
    elif num_results > 1:
        # there should only be one User with this email...
        # if there are more, we have a data error!
        raise NonUniqueEmail(email)
    else:
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            user = None
    return user

def authenticate_user(username, password):
    # reuse form-model logic in AuthenticationForm
    auth_dict = {
        'username' : username,
        'password' : password,
    }
    auth_form = AuthenticationForm(None, auth_dict)
    is_valid = auth_form.is_valid() # just run the validation
    auth_user = auth_form.get_user()
    return auth_user

def authenticate_user_by_email(email, password):
    existing_user = get_user_by_email(email, auth=True)
    if existing_user is not None:
        username = existing_user.username
        auth_user = authenticate_user(username, password)
    else:
        auth_user = None
    return auth_user

def authenticate_user_by_username_email(username_email, password):
    if email_re.search(username_email):
        email = username_email
        auth_user = authenticate_user_by_email(email, password)
    else:
        username = username_email
        auth_user = authenticate_user(username, password)
    return auth_user

def get_user_email(user, email):
    try:
        user_email = UserEmail.objects.get(user=user, email=email)
    except UserEmail.DoesNotExist:
        user_email = None
    return user_email

def associate_user_email(user, email, domain=DEFAULT_EMAIL_SENDING_DOMAIN, confirmed=False):
    """Associates `email` with `user`

    Resulting UserEmail.is_confirmed = `confirmed`, default False

    Side effect: sends an activation email if `confirmed` == False

    Requires:
    `user` and `email` to be valid
    `email` cannot be confirmed by any other user
    `email` cannot already be associated with THIS `user`
    """
    user_email = None
    if user and email:
        existing_user = get_user_by_email(email)
        if existing_user is None or (user == existing_user and not(user.is_active)):
            # email address must not be associated to another account, or must be a new registration
            user_email = get_user_email(user, email)
            if user_email is None:
                user_email = UserEmail.objects.create(user=user, email=email, is_confirmed=confirmed)
            if confirmed or user_email.is_confirmed:
                # don't need to send activation email for a pre-confirmed address
                # pre-confirmed email can come from a social auth provider
                user_email.confirm_and_activate_account()
            elif not user_email.is_confirmed:
                user_email.send_activation_email(domain)
            else:
                pass
        else:
            # skip association
            # This email address is either:
            # a) already confirmed on another account
            # b) not already confirmed, and not a new registration
            pass

            # email already associated with user
            pass
    else:
        # invalid user or email
        pass

    return user_email

def extract_user_email(username_email):
    email = None
    if email_re.search(username_email):
        email = username_email
        user = get_user_by_email(email)
    else:
        username = username_email
        user = get_user_by_username(username)

    return (user, email,)
