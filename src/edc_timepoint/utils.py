from django.conf import settings


def get_enable_timepoint_checks() -> bool:
    return getattr(settings, "EDC_TIMEPOINT_ENABLE_CHECKS", True)
