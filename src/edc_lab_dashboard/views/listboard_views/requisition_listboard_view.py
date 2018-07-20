from django.conf import settings
from edc_constants.constants import YES

from ...model_wrappers import RequisitionModelWrapper
from ..listboard_filters import RequisitionListboardViewFilters
from .base_listboard_view import BaseListboardView


class RequisitionListboardView(BaseListboardView):

    listboard_model = settings.LAB_DASHBOARD_REQUISITION_MODEL

    form_action_url = 'requisition_form_action_url'
    listboard_template = 'requisition_listboard_template'
    listboard_url = 'requisition_listboard_url'
    listboard_view_filters = RequisitionListboardViewFilters()
    model_wrapper_cls = RequisitionModelWrapper
    navbar_selected_item = 'requisition'
    search_form_url = 'requisition_listboard_url'
    show_all = True

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(is_drawn=YES, clinic_verified=YES)
        return options
