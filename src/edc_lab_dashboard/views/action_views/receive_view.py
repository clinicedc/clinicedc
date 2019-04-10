from django.apps import apps as django_apps
from django.contrib import messages
from edc_dashboard.view_mixins import EdcViewMixin
from edc_constants.constants import YES
from edc_lab import Specimen
from edc_lab.site_labs import site_labs
from edc_lab.labels import AliquotLabel
from edc_utils import get_utcnow

from ...view_mixins import ProcessRequisitionViewMixin
from .action_view import ActionView


class ReceiveView(EdcViewMixin, ProcessRequisitionViewMixin, ActionView):

    post_action_url = "receive_listboard_url"
    valid_form_actions = ["receive", "receive_and_process"]
    label_cls = AliquotLabel
    specimen_cls = Specimen

    def process_form_action(self, request=None):
        if not self.selected_items:
            message = "Nothing to do. No items selected."
            messages.warning(self.request, message)
        if self.action == "receive":
            self.receive()
            self.create_specimens()
        elif self.action == "receive_and_process":
            self.receive()
            self.create_specimens()
            self.process(request)

    def receive(self):
        """Updates selected requisitions as received.
        """
        updated = 0
        for model in site_labs.requisition_models.values():
            model_cls = django_apps.get_model(model)
            updated += (
                model_cls.objects.filter(pk__in=self.selected_items, is_drawn=YES)
                .exclude(received=True)
                .update(received=True, received_datetime=get_utcnow())
            )
        if updated:
            message = f"{updated} requisitions received."
            messages.success(self.request, message)
        return updated

    def create_specimens(self):
        """Creates aliquots for each selected and received requisition.
        """
        for requisition in self.get_requisitions(
            pk__in=self.selected_items, received=True
        ):
            self.specimen_cls(requisition=requisition)
