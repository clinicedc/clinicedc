from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .url_config import UrlConfig

name = f'edc_dashboard.middleware.DashboardMiddleware'
if name not in settings.MIDDLEWARE:
    raise ImproperlyConfigured(f'Missing middleware. Expected {name}.')
