from django.contrib import messages
from edc_base.view_mixins import EdcBaseViewMixin
from edc_lab.models import Aliquot
from edc_lab.labels import AliquotLabel
from edc_label import add_job_results_to_messages

from ...view_mixins import ProcessRequisitionViewMixin
from .action_view import ActionView


class RequisitionView(EdcBaseViewMixin, ProcessRequisitionViewMixin, ActionView):

    post_action_url = "requisition_listboard_url"
    valid_form_actions = ["print_labels"]
    action_name = "requisition"
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == "print_labels":
            if not self.selected_items:
                message = "Nothing to do. No items have been selected."
                messages.warning(request, message)
            else:
                job_results = []
                for requisition in self.processed_requisitions:
                    aliquots = Aliquot.objects.filter(
                        requisition_identifier=requisition.requisition_identifier
                    ).order_by("count")
                    if aliquots:
                        pks = [obj.pk for obj in aliquots if obj.is_primary]
                        if pks:
                            job_results.append(
                                self.print_labels(pks=pks, request=request)
                            )
                        pks = [obj.pk for obj in aliquots if not obj.is_primary]
                        if pks:
                            job_results.append(
                                self.print_labels(pks=pks, request=request)
                            )
                for requisition in self.unprocessed_requisitions:
                    messages.error(
                        self.request,
                        "Unable to print labels. Requisition has not been "
                        f"processed. Got {requisition.requisition_identifier}",
                    )
                if job_results:
                    add_job_results_to_messages(request, job_results)
