import sys

from django.conf import settings

from .user_profile import UserProfile
from .role import Role
from .signals import (
    update_user_profile_on_post_save,
    update_user_groups_on_role_m2m_changed,
)


if settings.APP_NAME == "edc_auth" and (
    "test" in sys.argv or "runtests.py" in sys.argv
):
    from ..tests.models import *  # noqa
