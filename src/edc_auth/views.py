from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django_revision.revision import site_revision


class LoginView(BaseLoginView):
    template_name = "edc_auth/login.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Tests cookies."""
        kwargs.update(**self.extra_context)
        self.request.session.set_test_cookie()
        if not self.request.session.test_cookie_worked():
            messages.add_message(self.request, messages.ERROR, "Please enable cookies.")
        self.request.session.delete_test_cookie()
        return super().get_context_data(**kwargs)

    @property
    def extra_context(self):
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        try:
            allow_password_reset = settings.ALLOW_PASSWORD_RESET
        except AttributeError:
            allow_password_reset = None
        return {
            "edc_base_template": "edc_dashboard/base.html",
            "DEBUG": settings.DEBUG,
            "ALLOW_PASSWORD_RESET": allow_password_reset,
            "revision": site_revision.tag,
            "live_system": live_system,
            "INDEX_PAGE": getattr(settings, "INDEX_PAGE", None),
            "INDEX_PAGE_LABEL": getattr(settings, "INDEX_PAGE_LABEL", None),
        }


class LogoutView(BaseLogoutView):
    template_name = "edc_auth/login.html"
    next_page = settings.LOGOUT_REDIRECT_URL or "accounts/login"

    @property
    def extra_context(self) -> dict:
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        return {
            "DEBUG": settings.DEBUG,
            "edc_base_template": "edc_dashboard/base.html",
            "revision": site_revision.tag,
            "live_system": live_system,
            "INDEX_PAGE": getattr(settings, "INDEX_PAGE", None),
            "INDEX_PAGE_LABEL": getattr(settings, "INDEX_PAGE_LABEL", None),
        }
