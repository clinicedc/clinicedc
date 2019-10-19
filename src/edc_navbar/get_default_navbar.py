from django.conf import settings


def get_default_navbar():
    """Returns the default navbar name.
    """
    return getattr(settings, "EDC_NAVBAR_DEFAULT", f"{settings.APP_NAME}_dashboard")
