from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django_revision.revision import site_revision
from edc_dashboard.utils import get_bootstrap_version, get_template_path_with_bootstrap


class LogoutView(BaseLogoutView):
    template_name = f"edc_auth/bootstrap{get_bootstrap_version()}/login.html"
    next_page = "edc_auth/login"

    @property
    def extra_context(self) -> dict:
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        return {
            "DEBUG": settings.DEBUG,
            "edc_base_template": get_template_path_with_bootstrap("edc_dashboard/base.html"),
            "revision": site_revision.tag,
            "live_system": live_system,
            "INDEX_PAGE": getattr(settings, "INDEX_PAGE", None),
            "INDEX_PAGE_LABEL": getattr(settings, "INDEX_PAGE_LABEL", None),
        }
