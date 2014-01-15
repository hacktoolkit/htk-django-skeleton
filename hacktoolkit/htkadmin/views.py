import json

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from hacktoolkit.htkadmin.decorators import htk_staff_required

from htk.view_helpers import render_to_response_custom as _r

@htk_staff_required
def index(request):
    response = _r('htkadmin/index.html')
    return response
