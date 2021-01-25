from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .utils import insert_bootstrap_version, select_edc_template
from .url_config import UrlConfig
from .url_names import url_names

name = "edc_dashboard.middleware.DashboardMiddleware"
if name not in settings.MIDDLEWARE:
    raise ImproperlyConfigured(f"Missing middleware. Expected {name}.")
