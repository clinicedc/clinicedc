from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab.labels import AliquotLabel

from ...view_mixins import RequisitionViewMixin, ProcessViewMixin, ModelsViewMixin
from .action_view import ActionView


class ProcessView(EdcBaseViewMixin, ModelsViewMixin, RequisitionViewMixin,
                  ProcessViewMixin, ActionView, TemplateView):

    post_action_url = 'process_listboard_url'
    valid_form_actions = ['process']
    action_name = 'process'
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == 'process':
            self.process(request)
