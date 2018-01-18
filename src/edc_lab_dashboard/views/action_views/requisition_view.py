from django.contrib import messages
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab.labels import AliquotLabel
from edc_label import add_job_results_to_messages

from ...view_mixins import ModelsViewMixin
from .action_view import ActionView


class RequisitionView(EdcBaseViewMixin, ModelsViewMixin, ActionView, TemplateView):

    post_action_url = 'requisition_listboard_url'
    valid_form_actions = ['print_labels']
    action_name = 'requisition'
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == 'print_labels':
            job_results = []
            for requisition in self.requisitions:
                aliquots = (
                    self.aliquot_model.objects.filter(
                        requisition_identifier=requisition.requisition_identifier)
                    .order_by('count'))
                if aliquots:
                    job_results.extend(self.print_labels(
                        pks=[obj.pk for obj in aliquots if obj.is_primary],
                        request=request))

                    job_results.extend(self.print_labels(
                        pks=[obj.pk for obj in aliquots if not obj.is_primary],
                        request=request))
            for requisition in self.requisition_model.objects.filter(
                    processed=False, pk__in=self.selected_items):
                messages.error(
                    self.request,
                    'Unable to print labels. Requisition has not been '
                    f'processed. Got {requisition.requisition_identifier}')
            add_job_results_to_messages(request, job_results)

    @property
    def requisitions(self):
        return self.requisition_model.objects.filter(
            processed=True, pk__in=self.selected_items)
