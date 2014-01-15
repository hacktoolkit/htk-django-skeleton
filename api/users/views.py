import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from htk.api.utils import json_response
from htk.api.utils import json_response_error
from htk.api.utils import json_response_okay

@login_required
def suggest(request):
    """This API endpoint supports User autocomplete
    First retrieve from followers and following, then search all users
    """
    query = request.GET.get('q')
    if query:
        query = query.strip()
        user_results = User.objects.filter(username__istartswith=query)
        results = [
            {
                'username' : user.username,
            }
            for user in user_results
        ]
        obj = {
            'data' : {
                'results' : results,
            },
        }
        response = json_response(obj)
    else:
        response = json_response_error()
    return response
