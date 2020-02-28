from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django_revision.revision import site_revision
from edc_protocol import Protocol


class LogoutView(BaseLogoutView):
    next_page = "login"

    @property
    def extra_context(self):
        protocol = Protocol()
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        return {
            "DEBUG": settings.DEBUG,
            "copyright": protocol.copyright,
            "disclaimer": protocol.disclaimer,
            "institution": protocol.institution,
            "license": protocol.license,
            "revision": site_revision.tag,
            "project_name": protocol.project_name,
            "live_system": live_system,
            "INDEX_PAGE": getattr(settings, "INDEX_PAGE", None),
            "INDEX_PAGE_LABEL": getattr(settings, "INDEX_PAGE_LABEL", None),
        }
