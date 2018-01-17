from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ..view_mixins import EdcLabelViewMixin


class HomeView(EdcBaseViewMixin, NavbarViewMixin, EdcLabelViewMixin, TemplateView):

    template_name = 'edc_label/home.html'
    navbar_name = 'edc_label'
    navbar_selected_item = 'label'
