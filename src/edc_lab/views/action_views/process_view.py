from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..mixins import RequisitionViewMixin, ProcessViewMixin
from .base_action_view import BaseActionView, app_config


class ProcessView(RequisitionViewMixin, ProcessViewMixin, BaseActionView):

    post_url_name = app_config.process_listboard_url_name
    valid_form_actions = ['process']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'process':
            self.process()
