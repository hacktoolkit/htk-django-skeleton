import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from accounts.constants import *
from htk.api.utils import json_response
from htk.api.utils import json_response_error
from htk.api.utils import json_response_okay

@login_required
@require_POST
def avatar(request):
    json_data = json.loads(request.body)

    avatar_type = json_data['type']
    if avatar_type in AVATAR_TYPES:
        user = request.user
        profile = user.profile
        profile.avatar = avatar_type
        profile.save(update_fields=['avatar',])
        response = json_response_okay()
    else:
        response = json_response_error()

    return response
