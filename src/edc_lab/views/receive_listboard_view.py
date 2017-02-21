from django.apps import apps as django_apps

from .requisition_listboard_view import RequisitionListboardView


class ReceiveListboardView(RequisitionListboardView):

    empty_queryset_message = 'All specimens have been received'
    action = 'receive'
    action_url_name = 'edc-lab:receive_url'
    search_form_action_url_name = 'edc-lab:receive_listboard_url'
    navbar_item_selected = 'receive'

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).receive_listboard_template_name]
