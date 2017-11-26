from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_constants.constants import YES

from ...model_wrappers import RequisitionModelWrapper
from ..listboard_filters import RequisitionListboardViewFilters
from ..mixins import StudySiteNameQuerysetViewMixin
from .base_listboard_view import BaseListboardView

app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class RequisitionListboardView(StudySiteNameQuerysetViewMixin, BaseListboardView):

    navbar_selected_item = 'requisition'

    model = edc_lab_app_config.requisition_model
    model_wrapper_cls = RequisitionModelWrapper
    listboard_url = 'requisition_listboard_url'
    listboard_template = 'requisition_listboard_template'
    show_all = True
    listboard_view_filters = RequisitionListboardViewFilters()
    form_action_url = 'requisition_action_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(is_drawn=YES)
        return options
