import warnings
from typing import Any

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django_revision.views import RevisionMixin
from edc_sites.view_mixins import SiteViewMixin

from .message_view_mixin import MessageViewMixin
from .template_request_context_mixin import TemplateRequestContextMixin


class EdcViewMixin(
    LoginRequiredMixin,
    MessageViewMixin,
    RevisionMixin,
    SiteViewMixin,
    TemplateRequestContextMixin,
):
    """Adds common template variables and warning messages."""

    edc_device_app: str = "edc_device"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        try:
            edc_device_app_config = django_apps.get_app_config(self.edc_device_app)
        except LookupError as e:
            edc_device_app_config = None
            warnings.warn(str(e))
        live_system = getattr(settings, "LIVE_SYSTEM", "TEST")
        kwargs.update(
            {
                "device_id": getattr(edc_device_app_config, "device_id", "device_id?"),
                "device_role": getattr(edc_device_app_config, "device_role", "device_role?"),
                "live_system": live_system,
            }
        )
        self.check_for_warning_messages(live_system=live_system)
        return super().get_context_data(**kwargs)

    def check_for_warning_messages(self, live_system=None) -> None:
        is_debug = getattr(settings, "DEBUG", False)

        msgs = []
        if is_debug:
            msgs.append(
                _(
                    "This EDC is running in DEBUG-mode. Use for testing only. "
                    "Do not use this system for production data collection!"
                )
            )
        elif not live_system:
            msgs.append(
                _(
                    "This EDC is for testing only. "
                    "Do not use this system for production data collection!"
                )
            )

        if self.request.user.is_superuser:
            msgs.append(
                _(
                    "You are using a `superuser` account. The EDC does not operate correctly "
                    "with user acounts that have the `superuser` status. "
                    "Update your user account before continuing."
                )
            )
        for msg in msgs:
            if msg not in [str(m) for m in messages.get_messages(self.request)]:
                messages.add_message(self.request, messages.ERROR, msg)

        warning_message = getattr(settings, "WARNING_MESSAGE", False)
        if warning_message and warning_message not in [
            str(m) for m in messages.get_messages(self.request)
        ]:
            messages.add_message(
                self.request, messages.WARNING, warning_message, extra_tags="warning"
            )
