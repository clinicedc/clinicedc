from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView
from django_revision.revision import site_revision
from edc_dashboard.utils import get_template_path_with_bootstrap


class LoginView(BaseLoginView):

    template_name = f"edc_auth/bootstrap{settings.EDC_BOOTSTRAP}/login.html"

    def get_context_data(self, **kwargs):
        """Tests cookies.
        """
        self.request.session.set_test_cookie()
        if not self.request.session.test_cookie_worked():
            messages.add_message(self.request, messages.ERROR, "Please enable cookies.")
        self.request.session.delete_test_cookie()
        return super().get_context_data(**kwargs)

    @property
    def extra_context(self):
        app_config = django_apps.get_app_config("edc_protocol")
        try:
            live_system = settings.LIVE_SYSTEM
        except AttributeError:
            live_system = None
        try:
            allow_password_reset = settings.ALLOW_PASSWORD_RESET
        except AttributeError:
            allow_password_reset = None
        return {
            "edc_base_template": get_template_path_with_bootstrap(
                "edc_dashboard/base.html"
            ),
            "DEBUG": settings.DEBUG,
            "ALLOW_PASSWORD_RESET": allow_password_reset,
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
