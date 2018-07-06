from django.contrib import messages
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab import AliquotLabel
from edc_lab.models import Aliquot
from edc_label import add_job_results_to_messages

from .action_view import ActionView
from ...view_mixins import RequisitionModelViewMixin


class RequisitionView(EdcBaseViewMixin, RequisitionModelViewMixin, ActionView):

    post_action_url = 'requisition_listboard_url'
    valid_form_actions = ['print_labels']
    action_name = 'requisition'
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == 'print_labels':
            if not self.selected_items:
                message = ('Nothing to do. No items have been selected.')
                messages.warning(request, message)
            else:
                job_results = []
                for requisition in self.requisitions:
                    aliquots = (
                        Aliquot.objects.filter(
                            requisition_identifier=requisition.requisition_identifier)
                        .order_by('count'))
                    if aliquots:
                        pks = [obj.pk for obj in aliquots if obj.is_primary]
                        if pks:
                            job_results.append(self.print_labels(
                                pks=pks, request=request))
                        pks = [obj.pk for obj in aliquots if not obj.is_primary]
                        if pks:
                            job_results.append(self.print_labels(
                                pks=pks, request=request))
                for requisition in self.requisition_model.objects.filter(
                        processed=False, pk__in=self.selected_items):
                    messages.error(
                        self.request,
                        'Unable to print labels. Requisition has not been '
                        f'processed. Got {requisition.requisition_identifier}')
                if job_results:
                    add_job_results_to_messages(request, job_results)

    @property
    def requisitions(self):
        return self.requisition_model.objects.filter(
            processed=True, pk__in=self.selected_items)
