from django.views.generic.base import TemplateView
from edc_dashboard.utils import get_bootstrap_version
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = f"edc_randomization/bootstrap{get_bootstrap_version()}/home.html"
    navbar_name = "edc_randomization"
    navbar_selected_item = "edc_randomization"
