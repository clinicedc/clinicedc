from typing import Any

from django.views.generic.base import ContextMixin

from edc_protocol import Protocol


class EdcProtocolViewMixin(ContextMixin):
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        protocol = Protocol()
        kwargs.update(
            {
                "protocol": protocol.protocol,
                "protocol_number": protocol.protocol_number,
                "protocol_name": protocol.protocol_name,
                "protocol_title": protocol.protocol_title,
            }
        )
        return super().get_context_data(**kwargs)
