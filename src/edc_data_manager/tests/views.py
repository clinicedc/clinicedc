from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar.view_mixin import NavbarViewMixin
from django.views.generic.base import TemplateView


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):

    template_name = "data_manager_app/home.html"
    navbar_name = "data_manager_app"
    navbar_selected_item = "data_manager_app"
