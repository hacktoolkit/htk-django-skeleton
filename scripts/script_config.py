# config.py
# shared settings for standalone scripts hooking into Django

import datetime
import os
import re
import sys

sys.stdout = sys.stderr

SCRIPTS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.realpath(os.path.join(SCRIPTS_DIR, '..').replace('\\', '/')))
sys.path.append(os.path.realpath(os.path.join(SCRIPTS_DIR, '..', '..').replace('\\', '/')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'hacktoolkit.settings'

# import rollbar so we can report stuff!
import rollbar

def job_runner(f):
    """Accepts any callable function and runs it

    Catches any exceptions and logs to Rollbar
    """
    try:
        f()
    except:
        rollbar.report_exc_info(sys.exc_info())

def slog(m):
    print '%s:%s\t%s' % (__file__, datetime.datetime.now().isoformat(), m,)
