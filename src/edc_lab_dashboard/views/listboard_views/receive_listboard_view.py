from django.apps import apps as django_apps
from django.urls import reverse
from django.utils.safestring import mark_safe
from edc_constants.constants import YES

# from ...dashboard_templates import dashboard_templates
from ...dashboard_urls import dashboard_urls
from .requisition_listboard_view import RequisitionListboardView

app_config = django_apps.get_app_config('edc_lab_dashboard')


class ReceiveListboardView(RequisitionListboardView):

    navbar_selected_item = 'receive'
    listboard_url = 'receive_listboard_url'
    listboard_template = 'receive_listboard_template'
    process_listboard_url = dashboard_urls.get('process_listboard_url')
    show_all = True
    form_action_url = 'receive_action_url'
    action_name = 'receive'

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(
            {'is_drawn': YES, 'received': False, 'processed': False})
        return options

    @property
    def empty_queryset_message(self):
        href = reverse(dashboard_urls.get('process_listboard_url'))
        return mark_safe(
            'All specimens have been received. Continue to '
            f'<a href="{href}" class="alert-link">processing</a>')
