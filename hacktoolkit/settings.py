# Django settings for hacktoolkit project.

import os
import rollbar
import re
import sys
from socket import gethostname

SERVER_HOSTNAME=gethostname()

BASEDIR = os.path.join(os.path.dirname(__file__), '..')
DIRMATCH = re.match('^(/home/(.*))/sites', BASEDIR)
HOMEDIR = DIRMATCH.group(1)
USER = DIRMATCH.group(2)
CREDENTIALS_DIR = os.path.join(HOMEDIR, 'credentials')

sys.path.append(CREDENTIALS_DIR)
import HtkDBCredentials

ENV_DEV = not(re.match('^/home/deploy.*', HOMEDIR))
ENV_QA = not ENV_DEV and SERVER_HOSTNAME == 'qa.hacktoolkit.com'
ENV_ALPHA = not ENV_DEV and SERVER_HOSTNAME == 'alpha.hacktoolkit.com'
ENV_STAGE = not ENV_DEV and SERVER_HOSTNAME == 'stage.hacktoolkit.com'
ENV_PROD = not ENV_DEV and not ENV_QA and not ENV_ALPHA and not ENV_STAGE

DEBUG = False           
if ENV_DEV:
    DEBUG = True
TEMPLATE_DEBUG = DEBUG

TEST = 'test' in sys.argv

# Set AUTH_PROFILE_MODULE to enable `user.get_profile()` hook
AUTH_PROFILE_MODULE = 'accounts.UserProfile'
CACHE_TIMEOUTS = {
    'user_obj': 30, #hold on to any given user-specific piece of information for no more than 30 minutes
}

ADMINS = (
    ('Hacktoolkit Info', 'info@hacktoolkit.com'),
)

ALLOWED_HOSTS = [
    '*',
]

MANAGERS = ADMINS

################################################################################
# DATABASES

if TEST:
    # in-memory SQLite used for testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    }
elif ENV_DEV:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': HtkDBCredentials.DB_NAME,     # Or path to database file if using sqlite3.
            'USER': HtkDBCredentials.DB_USER,     # Not used with sqlite3.
            'PASSWORD': HtkDBCredentials.DB_PASS, # Not used with sqlite3.
            'HOST': '',                              # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                              # Set to empty string for default. Not used with sqlite3.
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': HtkDBCredentials.DB_NAME,     # Or path to database file if using sqlite3.
            'USER': HtkDBCredentials.DB_USER,     # Not used with sqlite3.
            'PASSWORD': HtkDBCredentials.DB_PASS, # Not used with sqlite3.
            'HOST': '',                              # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                              # Set to empty string for default. Not used with sqlite3.
        },
        'master': {
            'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': HtkDBCredentials.DB_NAME,     # Or path to database file if using sqlite3.
            'USER': HtkDBCredentials.DB_USER,     # Not used with sqlite3.
            'PASSWORD': HtkDBCredentials.DB_PASS, # Not used with sqlite3.
            'HOST': '',                              # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                              # Set to empty string for default. Not used with sqlite3.
        }
    }

# https://docs.djangoproject.com/en/1.5/topics/db/multi-db/#automatic-database-routing
DATABASE_ROUTERS = ['hacktoolkit.database_routers.MasterSlaveRouter'] if not ENV_DEV else []

# end DATABASES
################################################################################

################################################################################
# CACHES
if TEST:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
elif ENV_DEV:
    CACHES = {
        'default' : {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#            'BACKEND' : 'redis_cache.cache.RedisCache',
            'LOCATION' : '127.0.0.1:6379:1',
            'OPTIONS' : {
                'PASSWORD' : 'REDIS_CACHE_PW',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
            }
        },
        'dummy': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }

    }
elif ENV_ALPHA or ENV_QA:
    CACHES = {
        'default' : {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#            'BACKEND' : 'redis_cache.cache.RedisCache',
            'LOCATION' : '127.0.0.1:6379:2',
            'OPTIONS' : {
                'PASSWORD' : 'REDIS_CACHE_PW',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
            }
        },
    }
elif ENV_STAGE or ENV_PROD:
    CACHES = {
    }

# end CACHES
################################################################################

################################################################################
# PASSWORD_HASHERS

# Use bcrypt as default password hasher, more secure
# https://docs.djangoproject.com/en/1.5/topics/auth/passwords/#using-bcrypt-with-django
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)
# end PASSWORD_HASHERS
################################################################################

DEFAULT_FROM_EMAIL = 'info@hacktoolkit.com'
#AUTH_USER_MODEL = 'auth.User'
#SOCIAL_AUTH_USER_MODEL = 'auth.User'
#AUTH_PROFILE_MODULE = 'accounts.UserProfile'
LOGIN_URL = '/account/login'
LOGIN_REDIRECT_URL = '/account'
#LOGIN_ERROR_URL = '/account/login_error'
LOGIN_ERROR_URL = LOGIN_URL

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASEDIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'p7#uo3nfov14$9a*hx6q83eb5+ae9b9dhhn@p9c05*&_@2k59s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'htk.middleware.GlobalRequestMiddleware',
    'htk.middleware.AllowedHostsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'htk.apps.prelaunch.middleware.PrelaunchModeMiddleware',
    'htk.middleware.TimezoneMiddleware',
    'htk.apps.accounts.middleware.HtkSocialAuthExceptionMiddleware',
    'htk.middleware.RewriteJsonResponseContentTypeMiddleware',
)

if not TEST:
    MIDDLEWARE_CLASSES += (
        'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
    )

ROOT_URLCONF = 'hacktoolkit.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, 'templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    # django built-ins
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # admin extentions
    'grappelli',
    'south',
    'redis_status',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    #'django.contrib.admindocs',
    # my apps
    'accounts',
    'api',
    'hacktoolkit',
    'htk',
    'htk.apps.feedback',
    'htk.apps.prelaunch',
    'scripts',
    # 3rd party
    'social.apps.django_app.default',
)

if TEST:
    INSTALLED_APPS += (
        'htk.test_scaffold',
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#####
# begin htk settings

HTK_ALLOWED_HOST_REGEXPS = (
    r'(.*\.)?hacktoolkit\.com(\.)?',
    r'django\.jontsai\.com(\.)?',
)
HTK_DEFAULT_DOMAIN = 'hacktoolkit.com'

HTK_DEFAULT_EMAIL_SENDING_DOMAIN = HTK_DEFAULT_DOMAIN
HTK_DEFAULT_EMAIL_SENDER = 'Hacktoolkit <info@hacktoolkit.com>'
HTK_DEFAULT_EMAIL_RECIPIENTS = ['info@hacktoolkit.com',]
HTK_DEFAULT_EMAIL_BCC = (
    'watcher@hacktoolkit.com',
)

HTK_ACCOUNTS_DEFAULT_DISPLAY_NAME = 'Hacktoolkit User'

HTK_CACHE_KEY_PREFIX = 'hacktoolkit'

HTK_EMAIL_CONTEXT_GENERATOR = 'htk.mailers.email_context_generator'

HTK_FEEDBACK_EMAIL_SUBJECT = 'New feedback from Hacktoolkit.com'
HTK_FEEDBACK_EMAIL_TO = (
    'Hacktoolkit <hello@hacktoolkit.com>',
)

HTK_PRELAUNCH_MODE = True
HTK_PRELAUNCH_TEMPLATE = 'htk/prelaunch.html'
HTK_PRELAUNCH_VIEW_CONTEXT_GENERATOR = 'hacktoolkit.view_helpers.wrap_data'

HTK_PRELAUNCH_EMAIL_TEMPLATE = 'htk/prelaunch'
HTK_PRELAUNCH_EMAIL_SUBJECT = 'Thanks for signing up at Hacktoolkit!'
HTK_PRELAUNCH_EMAIL_BCC = (
    '<hello@hacktoolkit.com>',
)

HTK_LIB_GEOIP_COUNTRY_DB = os.path.join(BASEDIR, '..', 'conf', 'geoip', 'GeoIP.dat')
HTK_LIB_GEOIP_CITY_DB = os.path.join(BASEDIR, '..', 'conf', 'geoip', 'GeoIPCity.dat')

HTK_SOCIAL_AUTH_CONNECT_ERROR_URL = '/account/settings'

# end htk settings
#####


#####
# begin python-social-auth settings
# http://psa.matiasaguirre.net/
# https://github.com/omab/python-social-auth
#
# Formerly django-social-auth
# http://django-social-auth.readthedocs.org/ 
# https://github.com/omab/django-social-auth

# http://psa.matiasaguirre.net/docs/configuration/settings.html#authentication-backends
AUTHENTICATION_BACKENDS = (
#    'social.backends.open_id.OpenIdAuth',
#    'social.backends.google.GoogleOpenId',
#    'social.backends.google.GoogleOAuth2',
#    'social.backends.google.GoogleOAuth',
    'social.backends.twitter.TwitterOAuth',
#    'social.backends.yahoo.YahooOpenId',
#    'social.backends.stripe.StripeOAuth2',
#    'social.backends.persona.PersonaAuth',
    'social.backends.facebook.FacebookOAuth2',
#    'social.backends.facebook.FacebookAppOAuth2',
#    'social.backends.yahoo.YahooOAuth',
#    'social.backends.angel.AngelOAuth2',
#    'social.backends.behance.BehanceOAuth2',
#    'social.backends.bitbucket.BitbucketOAuth',
#    'social.backends.box.BoxOAuth2',
#    'social.backends.linkedin.LinkedinOAuth',
#    'social.backends.linkedin.LinkedinOAuth2',
#    'social.backends.github.GithubOAuth2',
#    'social.backends.foursquare.FoursquareOAuth2',
#    'social.backends.instagram.InstagramOAuth2',
#    'social.backends.live.LiveOAuth2',
#    'social.backends.vk.VKOAuth2',
#    'social.backends.dailymotion.DailymotionOAuth2',
#    'social.backends.disqus.DisqusOAuth2',
#    'social.backends.dropbox.DropboxOAuth',
#    'social.backends.evernote.EvernoteSandboxOAuth',
#    'social.backends.fitbit.FitbitOAuth',
#    'social.backends.flickr.FlickrOAuth',
#    'social.backends.livejournal.LiveJournalOpenId',
#    'social.backends.soundcloud.SoundcloudOAuth2',
#    'social.backends.thisismyjam.ThisIsMyJamOAuth1',
#    'social.backends.stocktwits.StocktwitsOAuth2',
#    'social.backends.tripit.TripItOAuth',
#    'social.backends.twilio.TwilioAuth',
#    'social.backends.xing.XingOAuth',
#    'social.backends.yandex.YandexOAuth2',
#    'social.backends.douban.DoubanOAuth2',
#    'social.backends.mixcloud.MixcloudOAuth2',
#    'social.backends.rdio.RdioOAuth1',
#    'social.backends.rdio.RdioOAuth2',
#    'social.backends.yammer.YammerOAuth2',
#    'social.backends.stackoverflow.StackoverflowOAuth2',
#    'social.backends.readability.ReadabilityOAuth',
#    'social.backends.skyrock.SkyrockOAuth',
#    'social.backends.tumblr.TumblrOAuth',
#    'social.backends.reddit.RedditOAuth2',
#    'social.backends.steam.SteamOpenId',
#    'social.backends.podio.PodioOAuth2',
#    'social.backends.amazon.AmazonOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# http://psa.matiasaguirre.net/docs/backends/twitter.html
SOCIAL_AUTH_TWITTER_KEY         = ''
SOCIAL_AUTH_TWITTER_SECRET      = ''
# http://psa.matiasaguirre.net/docs/backends/facebook.html
SOCIAL_AUTH_FACEBOOK_KEY        = ''
SOCIAL_AUTH_FACEBOOK_SECRET     = ''
SOCIAL_AUTH_FACEBOOK_EXTENDED_PERMISSIONS = ['email']

# http://psa.matiasaguirre.net/docs/configuration/settings.html#urls-options
# login urls
# custom redirect url, default: same as LOGIN_REDIRECT_URL
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/account'
# newly registered users
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/account'
# login error
SOCIAL_AUTH_LOGIN_ERROR_URL = LOGIN_ERROR_URL
# newly associated accounts
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/account/settings'
# account disconnections
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account/settings'
# authentication and association complete
#SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'

# The user_details pipeline processor will set certain fields on user objects, such as email. Set this to a list of fields you only want to set for newly created users and avoid updating on further logins.
SOCIAL_AUTH_PROTECTED_USER_FIELDS = [
    'email', # don't let social auth overwrite primary email
]

# session expiration time
#SOCIAL_AUTH_EXPIRATION = 'expires'
# disable expiration configuration
SOCIAL_AUTH_SESSION_EXPIRATION = False

# disable user creations by django-social-auth
#SOCIAL_AUTH_CREATE_USERS = False # deprecated
# associate multiple user accounts with a single email address, disabled by default (False)
#SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True # deprecated

# send extra parameters on auth process by defining settings per provier
# e.g. to request Facebook to show Mobile authorization page, define:
# FACEBOOK_AUTH_EXTRA_ARGUMENTS = {'display': 'touch'}
# for other providers:
# <uppercase backend name>_AUTH_EXTRA_ARGUMENTS = {...}

# can send extra parameters on request token process
# <uppercase backend name>_REQUEST_TOKEN_EXTRA_ARGUMENTS = {...}

# allow redirects to different domains, disabled by default (True)
#SOCIAL_AUTH_SANITIZE_REDIRECTS = False

# redirect inactive users to a different page, Default: LOGIN_ERROR_URL
#SOCIAL_AUTH_INACTIVE_USER_URL = '...'

# override default exception logging behavior (logger or django.contrib.messages)
#SOCIAL_AUTH_PROCESS_EXCEPTIONS = 'social_auth.utils.process_exceptions'

# default SOCIAL_AUTH_PIPELINE, for reference
#SOCIAL_AUTH_PIPELINE = (
#    'social.pipeline.social_auth.social_details',
#    'social.pipeline.social_auth.social_uid',
#    'social.pipeline.social_auth.auth_allowed',
#    'social.pipeline.social_auth.social_user',
#    'social.pipeline.user.get_username',
#    'social.pipeline.user.create_user',
#    'social.pipeline.social_auth.associate_user',
#    'social.pipeline.social_auth.load_extra_data',
#    'social.pipeline.user.user_details'
#)

SOCIAL_AUTH_PIPELINE = (
    'accounts.social_auth_pipeline.reset_session_keys',
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'accounts.social_auth_pipeline.check_email',
    'accounts.social_auth_pipeline.check_incomplete_signup',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'accounts.social_auth_pipeline.associate_email',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'accounts.social_auth_pipeline.handle_new_user',
)

# end python-social-auth settings
#####

################################################################################
# Grappelli
# https://github.com/sehmaschine/django-grappelli
# http://django-grappelli.readthedocs.org/en/2.4.0/customization.html

GRAPPELLI_ADMIN_TITLE = 'Hacktoolkit Admin Site'

# end Grappelli
################################################################################

################################################################################
# rollbar.com (formerly ratchet.io)

ROLLBAR_ENV = USER if ENV_DEV else 'qa' if ENV_QA else 'alpha' if ENV_ALPHA else 'stage' if ENV_STAGE else 'production' if ENV_PROD else 'other'

ROLLBAR = {
    'access_token': 'ROLLBAR_ACCESS_TOKEN',
    'environment': ROLLBAR_ENV,
#    'branch': 'master',
#    'root': os.path.realpath(BASEDIR + '/..'),
}
rollbar.init(**ROLLBAR)

# end rollbar.com (formerly ratchet.io)
################################################################################

################################################################################
# emails through SendGrid

# send all emails via SendGrid, even dev
#if True or not ENV_DEV:
if False and not ENV_DEV:
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'SENDGRID_USERNAME'
    EMAIL_HOST_PASSWORD = 'SENDGRID_PASSWORD'
    EMAIL_PORT = 587
    EMAIL_USER_TLS = True

# end SendGrid
################################################################################
