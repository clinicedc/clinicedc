from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..dashboard_templates import dashboard_templates


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = dashboard_templates.get("home_template")
    navbar_name = "specimens"
    navbar_selected_item = "specimens"
