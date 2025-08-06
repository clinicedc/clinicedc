from django.conf import settings


def get_autodiscover():
    return getattr(settings, "EDC_NAVBAR_AUTODISCOVER", True)


def get_verify_on_load():
    return getattr(settings, "EDC_NAVBAR_VERIFY_ON_LOAD", "")
