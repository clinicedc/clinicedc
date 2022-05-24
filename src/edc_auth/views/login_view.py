from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView
from django_revision.revision import site_revision
from edc_dashboard.utils import get_template_path_with_bootstrap
from edc_protocol import Protocol


class LoginView(BaseLoginView):
    template_name = f"edc_auth/bootstrap{settings.EDC_BOOTSTRAP}/login.html"

    def get_context_data(self, **kwargs):
        """Tests cookies."""
        context = super().get_context_data(**kwargs)
        context.update(**self.extra_context)
        self.request.session.set_test_cookie()
        if not self.request.session.test_cookie_worked():
            messages.add_message(self.request, messages.ERROR, "Please enable cookies.")
        self.request.session.delete_test_cookie()
        return context

    @property
    def extra_context(self):
        protocol = Protocol()
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        try:
            allow_password_reset = settings.ALLOW_PASSWORD_RESET
        except AttributeError:
            allow_password_reset = None
        return {
            "edc_base_template": get_template_path_with_bootstrap("edc_dashboard/base.html"),
            "DEBUG": settings.DEBUG,
            "ALLOW_PASSWORD_RESET": allow_password_reset,
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
