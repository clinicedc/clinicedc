import os
from warnings import warn

from django.conf import settings
from django.template.loader import select_template


class EdcTemplateDoesNotExist(Exception):
    pass


def get_index_page() -> int:
    index_page = getattr(settings, "INDEX_PAGE", None)
    if not index_page:
        warn("Settings attribute not set. See settings.INDEX_PAGE")
    return getattr(settings, "INDEX_PAGE", None)


def get_index_page_label() -> int:
    return getattr(settings, "INDEX_PAGE_LABEL", settings.APP_NAME)


def splitall(path):
    """Taken from
    https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
    """
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        if parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        path = parts[0]
        allparts.insert(0, parts[1])
    return allparts


def select_edc_template(relative_path, default_app_label):
    """Returns a template object."""
    local_path = settings.APP_NAME
    default_path = default_app_label
    return select_template(
        [
            os.path.join(local_path, relative_path),
            os.path.join(default_path, relative_path),
        ]
    )


def get_dashboard_app_label():
    return getattr(settings, "EDC_DASHBOARD_APP_LABEL", None)
