from django.apps import apps as django_apps
from django.urls import reverse
from django.utils.safestring import mark_safe

from edc_constants.constants import YES

from .requisition_listboard_view import RequisitionListboardView

app_config = django_apps.get_app_config('edc_lab_dashboard')


class ProcessListboardView(RequisitionListboardView):

    empty_queryset_message = 'All specimens have been process'
    navbar_item_selected = 'process'
    listboard_url_name = app_config.process_listboard_url_name
    listboard_template_name = app_config.process_listboard_template_name
    form_action_url_name = f'edc_lab_dashboard:process_url'
    action_name = 'process'

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update({'is_drawn': YES, 'received': True, 'processed': False})
        return options

    @property
    def empty_queryset_message(self):
        href = reverse(self.pack_listboard_url_name)
        return mark_safe(
            'All specimens have been processed. Continue to '
            f'<a href="{href}" class="alert-link">packing</a>')
