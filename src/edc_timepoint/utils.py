from django.conf import settings


def get_enable_timepoint_checks() -> bool:
    return getattr(settings, "ENABLE_TIMEPOINT_CHECKS", True)
