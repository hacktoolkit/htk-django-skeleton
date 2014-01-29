import pytz

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext_lazy as _

from accounts.constants import *
from accounts.emails import password_reset_email
from accounts.session_keys import *
from accounts.utils import authenticate_user_by_username_email
from accounts.utils import associate_user_email
from accounts.utils import email_to_username_hash
from accounts.utils import get_user_by_email
from accounts.models import UserEmail
from accounts.models import UserProfile
from hacktoolkit.constants import *
from htk.utils.geo import get_us_state_abbreviation_choices

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label=_('Email'))

    class Meta:
        model = User
        fields = (
            'email',
        )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['username']
        self.fields['password2'].label = 'Confirm Password'
        for name, field in self.fields.items():
            if field.widget.__class__ in (forms.TextInput, forms.PasswordInput,):
                field.widget.attrs['class'] = 'pure-input-1'
                field.widget.attrs['placeholder'] = field.label

    def clean_email(self):
        email = self.cleaned_data['email']

        user = get_user_by_email(email)
        if user is not None:
            self.email = None
            raise forms.ValidationError(_("A user with that email already exists."))
        else:
            self.email = email
        return email

    def save(self, domain=DEFAULT_EMAIL_SENDING_DOMAIN, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        email = self.email
        # temporarily assign a unique username so that we can create the record and the user can log in
        user.username = email_to_username_hash(email)
        # we'll store the primary email in the User object
        user.email = email
        user.primary_email = email
        # require user to confirm email account before activating it
        user.is_active = False
        if commit:
            user.save()
            user_email = associate_user_email(user, email, domain)
        return user

class ResendConfirmationForm(forms.Form):
    email = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super(ResendConfirmationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            UserEmail.objects.get(email=email)
        except UserEmail.DoesNotExist:
            raise forms.ValidationError(_("A user with that email does not exist."))
        return email

class PasswordResetFormHtmlEmail(PasswordResetForm):
    def save(self,
             domain_override=None,
             subject_template_name='emails/password_reset_subject.txt',
             email_template_name='emails/reset_password.html',
             use_https=False,
             token_generator=default_token_generator,
             from_email=None,
             request=None):
        """Generates a one-use only link for resetting password and sends to the user
        """
        domain = request.get_host()
        for user in self.users_cache:
            password_reset_email(
                user,
                token_generator,
                use_https=use_https,
                domain=domain
            )

class UsernameEmailAuthenticationForm(forms.Form):
    """Based on django.contrib.auth.forms.AuthenticationForm
    """
    username_email = forms.CharField(label=_('Username or Email'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter the correct credentials. Note that password is case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(UsernameEmailAuthenticationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ in (forms.TextInput, forms.PasswordInput,):
                field.widget.attrs['class'] = 'pure-input-1'
                field.widget.attrs['placeholder'] = field.label

    def clean(self, username_email=None, password=None):
        """Clean the form and try to get user
        Parameterize username_email and password to allow invoking from subclass
        """
        if not username_email:
            username_email = self.cleaned_data.get('username_email')
        if not password:
            password = self.cleaned_data.get('password')

        if username_email and password:
            self.user_cache = authenticate_user_by_username_email(username_email, password)
        else:
            self.user_cache = None

        if self.user_cache is None:
            raise forms.ValidationError(self.error_messages['invalid_login'])
        elif not self.user_cache.is_active:
            raise forms.ValidationError(self.error_messages['inactive'])
        else:
            # all good, do nothing
            pass

        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(self.error_messages['no_cookies'])

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

################################################################################
# Social registration

class SocialRegistrationEmailForm(forms.Form):
    email = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super(SocialRegistrationEmailForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ in (forms.TextInput, forms.PasswordInput,):
                field.widget.attrs['class'] = 'pure-input-1'
                field.widget.attrs['placeholder'] = field.label

    def clean_email(self):
        email = self.cleaned_data['email']
        self.email = email
        return email

    def save(self, request):
        email = self.email
        request.session[SOCIAL_REGISTRATION_SETTING_EMAIL] = email
        return email

class SocialRegistrationAuthenticationForm(UsernameEmailAuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, email, *args, **kwargs):
        super(SocialRegistrationAuthenticationForm, self).__init__(None, *args, **kwargs)
        del self.fields['username_email']
        self.email = email

    def clean(self):
        email = self.email
        password = self.cleaned_data.get('password')
        return super(SocialRegistrationAuthenticationForm, self).clean(username_email=email, password=password)

################################################################################
# User settings

class TimezoneForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'timezone',
        )

    def save(self, user, request, commit=True):
        tz = self.cleaned_data['timezone']
        profile = user.profile
        profile.timezone = tz
        profile.save()
        django_timezone = pytz.timezone(tz)
        request.session[DJANGO_TIMEZONE] = django_timezone
        return tz

class AddEmailForm(forms.Form):
    add_email = forms.CharField(widget=forms.HiddenInput(attrs={'value': 1}))
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        user = get_user_by_email(email)
        if user is None:
            self.email = email
        else:
            raise forms.ValidationError('This email is already registered')

    def save(self, user=None, domain=DEFAULT_EMAIL_SENDING_DOMAIN, commit=True):
        user_email = None
        if user:
            email = self.email
            user_email = associate_user_email(user, email, domain)
        return user_email

class AbstractUpdateUserForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AbstractUpdateUserForm, self).__init__(*args, **kwargs)

    def get_user_obj(self):
        if self.user:
            user_obj = self.user
        else:
            user_obj = None
        return user_obj

    def save(self, commit=True):
        user_obj = self.get_user_obj()
        if user_obj and self.fields:
            for field in self.fields:
                value = self.cleaned_data[field]
                user_obj.__setattr__(field, value)
            user_obj.save(update_fields=self.fields)
        return user_obj

class AbstractUpdateUserProfileForm(AbstractUpdateUserForm):
    def get_user_obj(self):
        if self.user:
            user_obj = self.user.profile
        else:
            user_obj = None
        return user_obj

class UpdateUsernameForm(AbstractUpdateUserForm):
    class Meta:
        model = User
        fields = ('username',)

    def save(self, commit=True):
        user = super(UpdateUsernameForm, self).save(commit=True)
        user_profile = user.profile
        user_profile.has_username_set = True
        user_profile.save()
        return user

class UpdateUserFirstNameForm(AbstractUpdateUserForm):
    class Meta:
        model = User
        fields = ('first_name',)

class UpdateUserLastNameForm(AbstractUpdateUserForm):
    class Meta:
        model = User
        fields = ('last_name',)

class UpdateUserShareNameForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('share_name',)

class UpdateUserCityForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('city',)

class UpdateUserStateForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('state',)
        widgets = {
            'state': forms.widgets.Select(choices=get_us_state_abbreviation_choices()),
        }

class UpdateUserWebsiteForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('website',)

class UpdateUserFacebookForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('facebook',)

class UpdateUserTwitterForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('twitter',)

class UpdateUserBiographyForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('biography',)

class UpdateUserShareLocationForm(AbstractUpdateUserProfileForm):
    class Meta:
        model = UserProfile
        fields = ('share_location',)
