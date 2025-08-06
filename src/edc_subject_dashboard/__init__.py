from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

name = "edc_subject_dashboard.middleware.DashboardMiddleware"
if name not in settings.MIDDLEWARE:
    raise ImproperlyConfigured(f"Missing middleware. Expected {name}.")
