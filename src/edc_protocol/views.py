from typing import Any

from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from .trial_settings import trial_settings


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_protocol/home.html"
    navbar_name = "edc_protocol"
    navbar_selected_item = "protocol"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            {
                "protocol": trial_settings.protocol,
                "protocol_number": trial_settings.protocol_number,
                "protocol_name": trial_settings.protocol_name,
                "protocol_title": trial_settings.protocol_title,
                "study_open_datetime": trial_settings.study_open_datetime,
                "study_close_datetime": trial_settings.study_close_datetime,
            }
        )
        return super().get_context_data(**kwargs)
