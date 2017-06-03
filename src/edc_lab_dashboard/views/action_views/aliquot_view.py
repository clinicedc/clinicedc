from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_lab.labels import AliquotLabel

from .base_action_view import BaseActionView, app_config


class AliquotView(BaseActionView):

    post_url_name = app_config.aliquot_listboard_url_name
    valid_form_actions = ['print_labels']
    action_name = 'aliquot'
    label_class = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'print_labels':
            self.print_labels(pks=self.selected_items)
