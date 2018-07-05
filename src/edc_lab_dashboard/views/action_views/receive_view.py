from django.contrib import messages
from edc_base.utils import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import YES
from edc_lab import Specimen, AliquotLabel

from ...view_mixins import RequisitionViewMixin, ProcessViewMixin
from .action_view import ActionView


class ReceiveView(EdcBaseViewMixin, RequisitionViewMixin,
                  ProcessViewMixin, ActionView):

    post_action_url = 'receive_listboard_url'
    valid_form_actions = ['receive', 'receive_and_process']
    label_cls = AliquotLabel
    specimen_cls = Specimen

    def process_form_action(self, request=None):
        if not self.selected_items:
            message = ('Nothing to do. No items selected.')
            messages.warning(self.request, message)
        if self.action == 'receive':
            self.receive()
            self.create_specimens()
        elif self.action == 'receive_and_process':
            self.receive()
            self.create_specimens()
            self.process(request)

    def receive(self):
        """Updates selected requisitions as received.
        """
        updated = self.requisition_model.objects.filter(
            pk__in=self.requisitions, is_drawn=YES).exclude(
                received=True).update(
                    received=True, received_datetime=get_utcnow())
        if updated:
            message = (f'{updated} requisitions received.')
            messages.success(self.request, message)
        return updated

    def create_specimens(self):
        """Creates aliquots for each selected and recevied requisition.
        """
        for requisition in self.requisition_model.objects.filter(
                pk__in=self.requisitions, received=True):
            self.specimen_cls(requisition=requisition)
