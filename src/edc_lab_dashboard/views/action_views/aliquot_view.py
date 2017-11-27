from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_lab.labels import AliquotLabel

from .action_view import ActionView


class AliquotView(ActionView):

    post_action_url = 'aliquot_listboard_url'
    valid_form_actions = ['print_labels']
    action_name = 'aliquot'
    label_cls = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'print_labels':
            self.print_labels(pks=self.selected_items)
