from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from htk.session_keys import *
from htk.view_helpers import render_to_response_custom as _r
from hacktoolkit.view_helpers import wrap_data

def index(request):
    response = redirect('home')
    return response

def home(request):
    data = wrap_data(request)
    response = _r('home.html', data)
    return response

def about(request):
    data = wrap_data(request)
    response = _r('about.html', data)
    return response

def help(request):
    data = wrap_data(request)
    response = _r('help.html', data)
    return response

def tos(request):
    data = wrap_data(request)
    response = _r('tos.html', data)
    return response

def privacy(request):
    data = wrap_data(request)
    response = _r('privacy.html', data)
    return response

################################################################################
# meta

def error500(request):
    response = _r('500.html')
    return response

def error404(request):
    response = _r('404.html')
    return response
