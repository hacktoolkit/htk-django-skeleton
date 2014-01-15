from hashlib import sha1
import datetime
import pytz
import random
import rollbar
import sys

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.template import Context
from django.template import loader
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from social.apps.django_app.default.models import UserSocialAuth

from libraries.geoip.helpers import get_geoip_city
from libraries.geoip.helpers import get_geoip_country

from accounts.constants import *
from accounts.emails import activation_email
from accounts.emails import welcome_email

from hacktoolkit.constants import *
from htk.utils import utcnow

class UserProfile(models.Model):
    """
    django.contrib.auth.models.User does not have a unique email
    """
    user = models.OneToOneField(User, related_name='profile')

    share_name = models.BooleanField(default=False)
    has_username_set = models.BooleanField(default=False)
    timezone = models.CharField(max_length=64, choices=[(tz, tz,) for tz in pytz.common_timezones], blank=True, default='America/Los_Angeles')
    avatar = models.CharField(max_length=32, default='gravatar')
    website = models.CharField(max_length=128, blank=True)
    facebook = models.CharField(max_length=32, blank=True)
    twitter = models.CharField(max_length=32, blank=True)
    biography = models.TextField(max_length=2000, blank=True)

    address = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zipcode = models.CharField(max_length=5, blank=True)
    share_location = models.BooleanField(default=False)

    following = models.ManyToManyField(User, related_name='followers', blank=True)

    # tracking
    last_login_ip = models.CharField(max_length=15, blank=True)
    # http://en.wikipedia.org/wiki/ISO_3166-2
    detected_country = models.CharField(max_length=2, blank=True)
    detected_timezone = models.CharField(max_length=36, blank=True)
    # meta
    timestamp = models.DateTimeField(auto_now=True)

    # profile stuff
    def get_full_name(self):
        full_name = ' '.join([self.user.first_name, self.user.last_name,]).strip()
        return full_name

    def get_display_name(self):
        display_name = self.user.username if self.has_username_set else DEFAULT_DISPLAY_NAME

        if self.share_name:
            full_name = self.get_full_name()
            if full_name:
                display_name = full_name

        return display_name

    def get_nav_display_name(self):
        display_name = self.user.username if self.has_username_set else self.user.email

        return display_name

    def get_absolute_url(self):
        url = self.get_profile_url()
        return url

    def get_profile_url(self):
        url = None
        if self.has_username_set:
            url = reverse('profile', args=(self.user.username,))
        return url

    def get_tile_html(self):
        """Returns player_profile_tile HTML, as from API calls
        """
        template = loader.get_template('fragments/profiles/player_profile_tile.html')
        context = Context({ 'profile' : self, })
        html = template.render(context)
        return html

    ##
    # htk application stuff

    ##
    # meta and account stuff
    def activate(self):
        """Activate the User if not already activated
        """
        was_activated = False
        user = self.user
        if not user.is_active:
            user.is_active = True
            user.save()
            was_activated = user.is_active
        if was_activated:
            welcome_email(user)
        return was_activated

    def get_timezone(self):
        tz = self.timezone if self.timezone else DEFAULT_TIMEZONE
        return tz

    def get_django_timezone(self):
        tz = self.get_timezone()
        django_timezone = pytz.timezone(tz)
        return django_timezone

    def get_social_auths(self):
        """Gets all associated UserSocialAuth objects
        """
        social_auths = UserSocialAuth.objects.filter(user__id=self.user.id)
        return social_auths

    def get_social_user(self, provider):
        try:
            social_user = UserSocialAuth.objects.get(
                user__id=self.user.id,
                provider=provider
            )
        except UserSocialAuth.DoesNotExist:
            social_user = None
        return social_user

    def get_fb_social_user(self):
        """Gets a Facebook UserSocialAuth
        """
        social_user = self.get_social_user(SOCIAL_AUTH_PROVIDER_FACEBOOK)
        return social_user

    def get_fbid(self):
        """Gets a user's Facebook id
        """
        fbid = None
        social_user = self.get_fb_social_user()
        if social_user:
            fbid = social_user.uid
        return fbid

    def get_tw_social_user(self):
        """Gets a Twitter UserSocialAuth
        """
        social_user = self.get_social_user(SOCIAL_AUTH_PROVIDER_TWITTER)
        return social_user

    def get_twid(self):
        """Gets a user's Twitter id
        """
        twid = None
        social_user = self.get_tw_social_user()
        if social_user:
            twid = social_user.uid
        return twid

    def get_detected_country(self):
        country = self.detected_country or DEFAULT_COUNTRY
        return country

    def get_detected_timezone(self):
        tz = self.detected_timezone or DEFAULT_TIMEZONE
        return tz

    def set_primary_email(self, email):
        """Set the primary email address for `self.user`
        This is typically called from UserEmail.set_primary_email

        Assumes that there is no other auth.User with this email, so doesn't check
        """
        user = self.user
        user.email = email
        user.save()
        return user

    def update_locale_info_by_ip_from_request(self, request):
        """Update user info by IP Address
        
        Store last_login_ip only when logging in
        Store country resolved from IP
        Store timezone resolved from IP
        
        Caller: api.auth.decorators.register_or_login_user
        
        Unknown whether this code throws an exception, but catch it upstream if any
        """
        try:
            ip = extract_request_ip(request)
            if ip and self.last_login_ip != ip:
                self.last_login_ip = ip
                gi_country = get_geoip_country()
                gi_city = get_geoip_city()
                self.detected_country = gi_country.country_code_by_addr(ip)
                self.detected_timezone = gi_city.time_zone_by_addr(ip)
                self.save()
        except:
            #rollbar.report_exc_info(sys.exc_info(), request)
            pass

    ##
    # Access control and permissions
    def has_email(self, email):
        """Determine whether this User owns `email`
        """
        user_email = get_user_email(self.user, email)
        has_email = user_email and user_email.is_confirmed
        return has_email

    def is_htk_staff(self):
        """Determines whether this User is a Htk staff

        Staff list is in htk.htkadmin.constants
        User.is_staff=True is also considered a Htk staff
        """
        is_staff = False
        if self.user.is_staff:
            is_staff = True
        else:
            staff_map = get_htk_staff_id_email_map()
            staff_email = staff_map.get(self.user.id)
            if staff_email:
                is_staff = self.has_email(staff_email)
        return is_staff

    def __unicode__(self):
        #s = '%d: %s' % (self.user.id, self.user.email,)
        s = self.user.__unicode__()
        return s

    def save(self, **kwargs):
        """Any customizations,  like updating cache, etc
        """
        super(UserProfile, self).save(**kwargs)

class UserEmail(models.Model):
    """A User can have multiple email addresses using this table

    """
    user = models.ForeignKey(User, related_name='emails')
    email = models.EmailField(_('email address'))
    # set in self._reset_activation_key()
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(null=True, blank=True)

    is_confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        s = '%s, %s' % (self.user, self.email,)
        return s

    def _reset_activation_key(self, resend=False):
        """Resets the activation key

        `resend` whether this key is being reset as the result of a resend confirmation email

        If `resend`, then check the `key_expires` timestamp to see if we should reuse the existing activation key, or generate a new one
        """
        should_reset = True
        if resend and self.activation_key and self.key_expires:
            now = utcnow()
            if now < self.key_expires:
                # do not reset key if remaining time has not fallen below threshold
                remaining_time = self.key_expires - now
                threshold = datetime.timedelta(hours=EMAIL_ACTIVATION_KEY_REUSE_THRESHOLD_HOURS)
                should_reset = remaining_time < threshold

        if should_reset:
            user = self.user
            salt = sha1(str(random.random())).hexdigest()[:5]
            activation_key = sha1(salt + user.username).hexdigest()
            key_expires = utcnow() + datetime.timedelta(hours=EMAIL_ACTIVATION_KEY_EXPIRATION_HOURS)

            self.activation_key = activation_key
            self.key_expires = key_expires
            self.save()
        else:
            # no need to reset activation key, use the same one
            pass

    def set_primary_email(self):
        """Sets the primary email address of `self.user` to `self.email`
        """
        user = self.user
        if self.is_confirmed:
            # only able to set primary email address to this one if it has been confirmed
            email = self.email
            user = user.profile.set_primary_email(email)
        else:
            user = None
        return user

    def delete(self, *args, **kwargs):
        """Deletes this associated email address

        Can only be deleted if not the primary email address
        """
        user = self.user
        if user.email != self.email:
            super(UserEmail, self).delete(*args, **kwargs)
            result = True
        else:
            result = False
        return result

    def send_activation_email(self, domain=DEFAULT_EMAIL_SENDING_DOMAIN, resend=False):
        self._reset_activation_key(resend=resend)
        activation_email(self, domain=domain)

    def confirm_and_activate_account(self):
        """Confirms the email address, and activates the associated account if not already activated

        Side effect: Once an email address is confirmed by an account, no other accounts can have that email address in a pending (unconfirmed state)
        """
        # TODO: what if an account was purposefully deactivated? we should not activate it. but how would we know the difference?
        if not self.is_confirmed:
            self.is_confirmed = True
            self.save()
        was_activated = self.user.profile.activate()
        # purge all other records with same email addresses that aren't confirmed
        # NOTE: Be careful to not delete the wrong ones!
        UserEmail.objects.filter(email=self.email, is_confirmed=False).delete()
        return was_activated

    class Meta:
        verbose_name = 'User Email'
        unique_together = ('user', 'email',)

################################################################################
# signals and signal handlers

def create_user_profile(sender, instance, created, **kwargs):
    """signal handler for User post-save
    """
    if created:
        profile = UserProfile.objects.create(user=instance)
        profile.save()

def process_user_email_association(sender, instance, created, **kwargs):
    """signal handler for UserEmail post-save
    """
    user_email = instance
    if user_email.is_confirmed:
        user = user_email.user
        email = user_email.email

##
# signals

# Upon saving a User object, create a UserProfile object if it doesn't already exist
signals.post_save.connect(create_user_profile, sender=User)
# See AUTH_PROFILE_MODULE in settings.py

signals.post_save.connect(process_user_email_association, sender=UserEmail)

####################
# Import these last to prevent circular import
from accounts.utils import get_user_email
from hacktoolkit.htkadmin.utils import get_htk_staff_id_email_map
from htk.utils import extract_request_ip
