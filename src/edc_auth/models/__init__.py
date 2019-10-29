import sys

from django.conf import settings

from .user_profile import UserProfile
from .role import Role


if settings.APP_NAME == "edc_auth" and (
    "test" in sys.argv or "runtests.py" in sys.argv
):
    from ..tests.models import *  # noqa
