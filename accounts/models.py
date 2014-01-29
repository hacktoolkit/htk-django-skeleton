import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.template import Context
from django.template import loader

from htk.apps.accounts.models import AbstractUserProfile
from htk.apps.accounts.models import UserEmail

from accounts.constants import *
from accounts.emails import activation_email
from accounts.emails import welcome_email

from hacktoolkit.constants import *
from htk.utils import utcnow

class UserProfile(AbstractUserProfile):
    ##
    # Access control and permissions

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
from hacktoolkit.htkadmin.utils import get_htk_staff_id_email_map
