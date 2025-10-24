from django.conf import settings


def get_autodiscover():
    return getattr(settings, "EDC_NAVBAR_AUTODISCOVER", True)


def get_verify_on_load():
    return getattr(settings, "EDC_NAVBAR_VERIFY_ON_LOAD", "")


def get_register_default_navbar():
    return getattr(settings, "EDC_NAVBAR_REGISTER_DEFAULT_NAVBAR", True)


def get_default_navbar_name():
    """Returns the default navbar name.

    For example: inte_dashboard for project INTE.
    """
    return getattr(
        settings, "EDC_NAVBAR_DEFAULT_NAVBAR_NAME", f"{settings.APP_NAME}_dashboard".lower()
    )
