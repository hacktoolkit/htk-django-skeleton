from django.contrib.sitemaps import Sitemap

from accounts.models import UserProfile

class ProfilesSitemap(Sitemap):
    changefreq = 'hourly'
    priority = 0.5

    def items(self):
        profiles = UserProfile.objects.filter(has_username_set=True)
        return profiles

    def lastmod(self, obj):
        timestamp = obj.timestamp
        return timestamp
