from django.conf import settings

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware

class HtkSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def get_redirect_uri(self, request, exception):
        """Redirect to LOGIN_ERROR_URL by default
        Otherwise, go to the SOCIAL_AUTH_<STRATEGY>_LOGIN_ERROR_URL for that backend provider if specified

        However, if user is logged in when the exception occurred, always go to account settings
        """
        url = settings.LOGIN_ERROR_URL
        if request.user.is_authenticated():
            url = reverse('account_settings')
        return url
