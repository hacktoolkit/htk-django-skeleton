"""
WSGI config for hacktoolkit project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import re
import sys

sys.stdout = sys.stderr

WSGIDIR = os.path.dirname(__file__)
sys.path.append(os.path.realpath(os.path.join(WSGIDIR, '..').replace('\\', '/')))
#sys.path.append(os.path.realpath(os.path.join(WSGIDIR, '..', '..').replace('\\', '/')))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hacktoolkit.settings")

ENV_DEV = not(re.match('/home/deploy', WSGIDIR))

if ENV_DEV:
    sys.path.append(WSGIDIR)
    import monitor
    monitor.start(interval=1.0)

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
