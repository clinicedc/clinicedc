from django.conf import settings


def get_default_navbar():
    """Returns the default navbar name.

    For example: inte_dashboard for project INTE.
    """
    return settings.EDC_NAVBAR_DEFAULT
