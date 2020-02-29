from django.views.generic.base import ContextMixin
from edc_protocol import Protocol


class EdcProtocolViewMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        protocol = Protocol()
        context.update(
            {
                "protocol": protocol.protocol,
                "protocol_number": protocol.protocol_number,
                "protocol_name": protocol.protocol_name,
                "protocol_title": protocol.protocol_title,
            }
        )
        return context
