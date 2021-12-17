from django.conf import settings

if (
    "edc_navbar" in settings.INSTALLED_APPS
    or "edc_navbar.apps.AppConfig" in settings.INSTALLED_APPS
):
    administration = ["edc_navbar.nav_administration"]
else:
    administration = []
