from django.contrib import messages
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab.labels import AliquotLabel

from ...view_mixins import ProcessRequisitionViewMixin
from .action_view import ActionView


class ProcessView(EdcViewMixin, ProcessRequisitionViewMixin, ActionView):
    post_action_url = "process_listboard_url"
    valid_form_actions = ["process"]
    action_name = "process"
    label_cls = AliquotLabel

    def process_form_action(self, request=None):
        if self.action == "process":
            if not self.selected_items:
                message = "Nothing to do. No items have been selected."
                messages.warning(request, message)
            else:
                self.process(request)
