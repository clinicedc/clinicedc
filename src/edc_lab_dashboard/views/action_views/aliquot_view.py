from django.contrib import messages
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab.labels import AliquotLabel
from edc_label import add_job_results_to_messages, LabPrintersMixin

from .action_view import ActionView


class AliquotView(EdcViewMixin, LabPrintersMixin, ActionView):

    post_action_url = "aliquot_listboard_url"
    valid_form_actions = ["print_labels"]
    action_name = "aliquot"
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == "print_labels":
            if not self.selected_items:
                message = "Nothing to do. No items have been selected."
                messages.warning(request, message)
            else:
                job_result = self.print_labels(pks=self.selected_items, request=request)
                if job_result:
                    add_job_results_to_messages(request, [job_result])
                else:
                    messages.error(
                        request,
                        f"Failed to print. Selected items were {self.selected_items}.",
                    )
