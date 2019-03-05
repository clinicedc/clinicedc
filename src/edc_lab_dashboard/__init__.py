from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .dashboard_urls import dashboard_urls
from .dashboard_templates import dashboard_templates

name = f"edc_lab_dashboard.middleware.DashboardMiddleware"
if name not in settings.MIDDLEWARE:
    raise ImproperlyConfigured(f"Missing middleware. Expected {name}.")
