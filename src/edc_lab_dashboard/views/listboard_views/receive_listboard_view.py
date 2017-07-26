from django.urls import reverse
from django.utils.safestring import mark_safe

from edc_constants.constants import YES

from .base_listboard import app_config, app_name
from .requisition_listboard_view import RequisitionListboardView


class ReceiveListboardView(RequisitionListboardView):

    navbar_item_selected = 'receive'
    listboard_url_name = app_config.receive_listboard_url_name
    listboard_template_name = app_config.receive_listboard_template_name
    show_all = True
    form_action_url_name = f'{app_name}:receive_url'
    action_name = 'receive'

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(
            {'is_drawn': YES, 'received': False, 'processed': False})
        return options

    @property
    def empty_queryset_message(self):
        href = reverse(self.process_listboard_url_name)
        return mark_safe(
            'All specimens have been received. Continue to '
            f'<a href="{href}" class="alert-link">processing</a>')
