from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar.view_mixin import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_review_dashboard/bootstrap3/home.html"
    navbar_name = "edc_review_dashboard"
    navbar_selected_item = "edc_review_dashboard"
