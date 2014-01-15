from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from accounts.models import UserEmail
from accounts.models import UserProfile

from social.apps.django_app.default.models import UserSocialAuth

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    filter_horizontal = (
        'following',
    )

class UserEmailInline(admin.TabularInline):
    model = UserEmail
    extra = 0
    can_delete = True

class UserSocialAuthInline(admin.TabularInline):
    model = UserSocialAuth
    extra = 0
    can_delete = True

class UserProfileAdmin(UserAdmin):
#    readonly_fields = ('user',)
#    list_editable = ('display_name', 'limited')
    list_display = (
        'id',
        'username',
        'has_username_set',
        'email',
        'first_name',
        'last_name',
        'share_name',
        'timezone',
        'last_login_ip',
        'detected_country',
        'detected_timezone',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'profile__has_username_set',
        'profile__detected_country',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'facebook',
        'twitter',
    )

    inlines = [
        UserProfileInline,
        UserEmailInline,
        UserSocialAuthInline,
    ]

    def has_username_set(self, obj):
        try:
            return obj.profile.has_username_set
        except UserProfile.DoesNotExist:
            return False

    def share_name(self, obj):
        try:
            return obj.profile.share_name
        except UserProfile.DoesNotExist:
            return False

    def timezone(self, obj):
        try:
            return obj.profile.timezone
        except UserProfile.DoesNotExist:
            return False

    def last_login_ip(self, obj):
        try:
            return obj.profile.last_login_ip
        except UserProfile.DoesNotExist:
            return ''

    def detected_country(self, obj):
        try:
            return obj.profile.get_detected_country()
        except UserProfile.DoesNotExist:
            return ''
    def detected_timezone(self, obj):
        try:
            return obj.profile.get_detected_timezone()
        except UserProfile.DoesNotExist:
            return ''

# use custom UserProfileAdmin instead of the built-in UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
