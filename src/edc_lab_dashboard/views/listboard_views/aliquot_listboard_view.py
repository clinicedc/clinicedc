from django.apps import apps as django_apps


from ...model_wrappers import AliquotModelWrapper
from ..listboard_filters import AliquotListboardViewFilters
from .base_listboard_view import BaseListboardView

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class AliquotListboardView(BaseListboardView):

    form_action_url = 'aliquot_form_action_url'
    listboard_template = 'aliquot_listboard_template'
    listboard_url = 'aliquot_listboard_url'
    listboard_view_filters = AliquotListboardViewFilters()
    model = edc_lab_app_config.aliquot_model
    model_wrapper_cls = AliquotModelWrapper
    navbar_selected_item = 'aliquot'
    search_form_url = 'aliquot_listboard_url'
    show_all = True
