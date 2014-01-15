from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from accounts.sitemaps import ProfilesSitemap

# https://docs.djangoproject.com/en/1.5/ref/contrib/sitemaps/

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        view_names = [
            # general
            'home',
            # accounts
            'account_login',
            'account_register',
            'account_resend_confirmation',
            'account_forgot_password',
        ]
        return view_names

    def location(self, view_name):
        path = reverse(view_name)
        return path

SITEMAPS = {
    'static' : StaticViewSitemap,
}
