from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def htk_staff_required(view_func):
    """Decorator for views that require access by Hacktoolkit staff or Django staff user
    """
    @login_required
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.profile.is_htk_staff():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view
