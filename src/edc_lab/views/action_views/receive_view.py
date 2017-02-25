from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.utils import get_utcnow
from edc_constants.constants import YES

from ...lab import Specimen
from ..mixins import RequisitionViewMixin, ProcessViewMixin
from .base_action_view import BaseActionView, app_config


class ReceiveView(RequisitionViewMixin, ProcessViewMixin, BaseActionView):

    post_url_name = app_config.receive_listboard_url_name
    valid_form_actions = ['receive', 'receive_and_process']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'receive':
            self.receive()
            self.create_specimens()
        elif self.action == 'receive_and_process':
            self.receive()
            self.create_specimens()
            self.process()

    def receive(self):
        return self.requisition_model.objects.filter(
            pk__in=self.requisitions, is_drawn=YES).exclude(
                received=True).update(
                    received=True, received_datetime=get_utcnow())

    def create_specimens(self):
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True):
            Specimen(requisition=requisition)
