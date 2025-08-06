from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_export/home.html"
    navbar_name = "edc_export"
    navbar_selected_item = "export"
