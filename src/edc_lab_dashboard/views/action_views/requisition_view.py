from django.contrib import messages
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab.labels import RequisitionLabel
from edc_label import add_job_results_to_messages

from ...view_mixins import ProcessRequisitionViewMixin
from .action_view import ActionView


class RequisitionView(EdcViewMixin, ProcessRequisitionViewMixin, ActionView):

    post_action_url = "requisition_listboard_url"
    valid_form_actions = ["print_labels"]
    action_name = "requisition"
    label_cls = RequisitionLabel

    def process_form_action(self, request=None):
        if self.action == "print_labels":
            if not self.selected_items:
                message = "Nothing to do. No items have been selected."
                messages.warning(request, message)
            else:
                job_results = []
                pks = [
                    (obj._meta.label_lower, obj.pk)
                    for obj in self.get_requisitions(pk__in=self.selected_items)
                ]
                if pks:
                    job_results.append(self.print_labels(pks=pks, request=request))
                if job_results:
                    add_job_results_to_messages(request, job_results)
