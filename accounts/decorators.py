from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

def logged_in_redirect_home(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('account_home'))
        return view_func(request, *args, **kwargs)
    return wrapped_view

def logout_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            logout(request)
        return view_func(request, *args, **kwargs)
    return wrapped_view
