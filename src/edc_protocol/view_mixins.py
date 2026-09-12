from typing import Any

from django.views.generic.base import ContextMixin

from .trial_settings import trial_settings


class EdcProtocolViewMixin(ContextMixin):
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            {
                "protocol": trial_settings.protocol,
                "protocol_number": trial_settings.protocol_number,
                "protocol_name": trial_settings.protocol_name,
                "protocol_title": trial_settings.protocol_title,
            }
        )
        return super().get_context_data(**kwargs)
