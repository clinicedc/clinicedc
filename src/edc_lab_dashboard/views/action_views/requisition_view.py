from django.contrib import messages
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab.labels import AliquotLabel, RequisitionLabel
from edc_lab.models import Aliquot
from edc_label import add_job_results_to_messages

from ...view_mixins import ProcessRequisitionViewMixin
from .action_view import ActionView


class RequisitionView(EdcViewMixin, ProcessRequisitionViewMixin, ActionView):
    post_action_url = "requisition_listboard_url"
    valid_form_actions = ["print_labels", "print_aliquot_labels"]
    action_name = "requisition"
    label_cls = RequisitionLabel

    def process_form_action(self, request=None):
        if self.action in self.valid_form_actions:
            if not self.selected_items:
                message = "Nothing to do. No items have been selected."
                messages.warning(request, message)
            elif self.action == "print_labels":
                self._print_labels(request=request)
            elif self.action == "print_aliquot_labels":
                self._print_aliquot_labels(request=request)

    def _print_labels(self, request=None):
        job_results = []
        pks = [
            (obj._meta.label_lower, obj.pk)
            for obj in self.get_requisitions(pk__in=self.selected_items)
        ]
        if pks:
            job_results.append(self.print_labels(pks=pks, request=request))
        if job_results:
            add_job_results_to_messages(request, job_results)

    def _print_aliquot_labels(self, request=None):
        self.label_cls = AliquotLabel
        job_results = []
        for requisition in self.processed_requisitions:
            aliquots = Aliquot.objects.filter(
                requisition_identifier=requisition.requisition_identifier
            ).order_by("count")
            if aliquots:
                pks = [obj.pk for obj in aliquots if obj.is_primary]
                if pks:
                    job_results.append(self.print_labels(pks=pks, request=request))
                pks = [obj.pk for obj in aliquots if not obj.is_primary]
                if pks:
                    job_results.append(self.print_labels(pks=pks, request=request))
        for requisition in self.unprocessed_requisitions:
            messages.error(
                self.request,
                "Unable to print labels. Requisition has not been "
                f"processed. Got {requisition.requisition_identifier}",
            )
        if job_results:
            add_job_results_to_messages(request, job_results)
