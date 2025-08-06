from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar.view_mixin import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_visit_schedule/home.html"
    navbar_name = "edc_visit_schedule"
    navbar_selected_item = "visit_schedule"
