from typing import Any

from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from .research_protocol_config import ResearchProtocolConfig


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_protocol/home.html"
    navbar_name = "edc_protocol"
    navbar_selected_item = "protocol"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        protocol_config = ResearchProtocolConfig()
        kwargs.update(
            {
                "protocol": protocol_config.protocol,
                "protocol_number": protocol_config.protocol_number,
                "protocol_name": protocol_config.protocol_name,
                "protocol_title": protocol_config.protocol_title,
                "study_open_datetime": protocol_config.study_open_datetime,
                "study_close_datetime": protocol_config.study_close_datetime,
            }
        )
        return super().get_context_data(**kwargs)
