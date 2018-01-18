from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin

from ...view_mixins import ModelsViewMixin
from .action_view import ActionView


class BoxView(EdcBaseViewMixin, ModelsViewMixin, ActionView, TemplateView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'

    def form_actions(self):
        pass
