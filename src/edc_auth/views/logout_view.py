from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django_revision.revision import site_revision


class LogoutView(BaseLogoutView):

    next_page = "login"

    @property
    def extra_context(self):
        app_config = django_apps.get_app_config("edc_protocol")
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        return {
            "DEBUG": settings.DEBUG,
            "copyright": app_config.copyright,
            "disclaimer": app_config.disclaimer,
            "institution": app_config.institution,
            "license": app_config.license,
            "revision": site_revision.tag,
            "project_name": app_config.project_name,
            "live_system": live_system,
            "INDEX_PAGE": getattr(settings, "INDEX_PAGE", None),
            "INDEX_PAGE_LABEL": getattr(settings, "INDEX_PAGE_LABEL", None),
        }
