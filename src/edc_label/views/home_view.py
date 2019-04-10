from django.conf import settings
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..view_mixins import EdcLabelViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, EdcLabelViewMixin, TemplateView):

    template_name = f"edc_label/bootstrap{settings.EDC_BOOTSTRAP}/home.html"
    navbar_name = "edc_label"
    navbar_selected_item = "label"
