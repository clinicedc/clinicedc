from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_lab.labels import AliquotLabel

from ...view_mixins import RequisitionViewMixin, ProcessViewMixin
from .action_view import ActionView


class ProcessView(RequisitionViewMixin, ProcessViewMixin, ActionView):

    post_action_url = 'process_listboard_url'
    valid_form_actions = ['process']
    action_name = 'process'
    label_cls = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'process':
            self.process()
