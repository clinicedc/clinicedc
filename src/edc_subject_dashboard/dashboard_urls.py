import contextlib

from django.conf import settings

dashboard_urls = dict()

with contextlib.suppress(AttributeError):
    dashboard_urls.update(**settings.SUBJECT_DASHBOARD_URL_NAMES)
