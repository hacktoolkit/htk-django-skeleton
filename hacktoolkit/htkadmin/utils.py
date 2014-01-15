from accounts.utils import get_user_by_email
from hacktoolkit.htkadmin.cachekeys import HtkStaffCache
from hacktoolkit.htkadmin.constants import *

def get_htk_staff_id_email_map():
    """Gets a mapping of Htk staff

    Returns a dictionary mapping User ids to emails
    """
    c = HtkStaffCache()
    staff_map = c.get()
    if staff_map is None:
        staff_map = {}
        for email in HTK_STAFF_EMAILS:
            user = get_user_by_email(email)
            if user:
                staff_map[user.id] = email
        c.cache_store(staff_map)
    return staff_map
