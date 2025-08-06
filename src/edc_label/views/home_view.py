from typing import Any

from django.urls import reverse
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..view_mixins import EdcLabelViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, EdcLabelViewMixin, TemplateView):
    template_name = "edc_label/home.html"
    navbar_name = "edc_label"
    navbar_selected_item = "label"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        printer_setup_url = reverse("edc_label:printer_setup_url")
        kwargs.update(
            printer_setup_url=printer_setup_url,
        )
        return super().get_context_data(**kwargs)
