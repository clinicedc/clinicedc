from django.urls import reverse
from django.views.generic.base import TemplateView
from edc_dashboard.utils import get_bootstrap_version
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..view_mixins import EdcLabelViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, EdcLabelViewMixin, TemplateView):
    template_name = f"edc_label/bootstrap{get_bootstrap_version()}/home.html"
    navbar_name = "edc_label"
    navbar_selected_item = "label"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        printer_setup_url = reverse("edc_label:printer_setup_url")
        context.update(
            printer_setup_url=printer_setup_url,
        )
        return context
