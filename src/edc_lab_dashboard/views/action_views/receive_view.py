from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator

from edc_base.utils import get_utcnow
from edc_constants.constants import YES

from edc_lab.lab import Specimen
from edc_lab.labels import AliquotLabel

from ..mixins import RequisitionViewMixin, ProcessViewMixin
from .base_action_view import BaseActionView


app_config = django_apps.get_app_config('edc_lab_dashboard')


class ReceiveView(RequisitionViewMixin, ProcessViewMixin, BaseActionView):

    post_url_name = app_config.receive_listboard_url_name
    valid_form_actions = ['receive', 'receive_and_process']
    label_cls = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if not self.selected_items:
            message = ('Nothing to do. No items selected.')
            messages.warning(self.request, message)
        if self.action == 'receive':
            self.receive()
            self.create_specimens()
        elif self.action == 'receive_and_process':
            self.receive()
            self.create_specimens()
            self.process()

    def receive(self):
        """Updates selected requisitions as received.
        """
        updated = self.requisition_model.objects.filter(
            pk__in=self.requisitions, is_drawn=YES).exclude(
                received=True).update(
                    received=True, received_datetime=get_utcnow())
        if updated:
            message = ('{} requisitions received.'.format(updated))
            messages.success(self.request, message)
        return updated

    def create_specimens(self):
        """Creates aliquots for each selected and recevied requisition.
        """
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True):
            Specimen(requisition=requisition)
