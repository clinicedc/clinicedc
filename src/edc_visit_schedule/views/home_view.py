from django.conf import settings
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar.view_mixin import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = f"edc_visit_schedule/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_visit_schedule"
    navbar_selected_item = "visit_schedule"
