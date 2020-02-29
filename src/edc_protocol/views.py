from django.conf import settings
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol import Protocol


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = f"edc_protocol/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_protocol"
    navbar_selected_item = "protocol"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        protocol = Protocol()
        context.update(
            {
                "protocol": protocol.protocol,
                "protocol_number": protocol.protocol_number,
                "protocol_name": protocol.protocol_name,
                "protocol_title": protocol.protocol_title,
                "study_open_datetime": protocol.study_open_datetime,
                "study_close_datetime": protocol.study_close_datetime,
            }
        )
        return context
