from django.conf import settings


def holidays_disabled():
    return getattr(settings, "EDC_FACILITY_DISABLE_HOLIDAYS", False)
