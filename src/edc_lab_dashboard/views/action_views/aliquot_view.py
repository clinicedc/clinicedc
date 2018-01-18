from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab.labels import AliquotLabel

from ...view_mixins import ModelsViewMixin
from .action_view import ActionView


class AliquotView(EdcBaseViewMixin, ModelsViewMixin, ActionView, TemplateView):

    post_action_url = 'aliquot_listboard_url'
    valid_form_actions = ['print_labels']
    action_name = 'aliquot'
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == 'print_labels':
            self.print_labels(pks=self.selected_items, request=request)
