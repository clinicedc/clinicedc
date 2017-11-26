from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_lab.labels import AliquotLabel

from ..mixins import RequisitionViewMixin, ProcessViewMixin
from .base_action_view import BaseActionView


class ProcessView(RequisitionViewMixin, ProcessViewMixin, BaseActionView):

    post_url = 'process_listboard_url'
    valid_form_actions = ['process']
    action_name = 'process'
    label_cls = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'process':
            self.process()
