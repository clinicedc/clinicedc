from typing import Any

from django.views.generic.base import ContextMixin

from .research_protocol_config import ResearchProtocolConfig


class EdcProtocolViewMixin(ContextMixin):
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        protocol_config = ResearchProtocolConfig()
        kwargs.update(
            {
                "protocol": protocol_config.protocol,
                "protocol_number": protocol_config.protocol_number,
                "protocol_name": protocol_config.protocol_name,
                "protocol_title": protocol_config.protocol_title,
            }
        )
        return super().get_context_data(**kwargs)
