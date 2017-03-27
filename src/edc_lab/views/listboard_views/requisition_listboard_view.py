from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_constants.constants import YES
from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ..listboard_filters import RequisitionListboardViewFilters
from ..mixins import StudySiteNameQuerysetViewMixin
from .base_listboard import BaseListboardView, app_config, app_name


class RequisitionModelWrapper(ModelWrapper):

    model_name = app_config.requisition_model
    next_url_name = app_config.requisition_listboard_url_name


class RequisitionListboardView(StudySiteNameQuerysetViewMixin, BaseListboardView):

    navbar_item_selected = 'requisition'

    model_name = app_config.requisition_model
    model_wrapper_class = RequisitionModelWrapper
    listboard_url_name = app_config.requisition_listboard_url_name
    listboard_template_name = app_config.requisition_listboard_template_name
    show_all = True
    listboard_view_filters = RequisitionListboardViewFilters()
    form_action_url_name = '{}:requisition_url'.format(app_name)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(is_drawn=YES)
        return options
