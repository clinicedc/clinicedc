from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_constants.constants import YES
from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from .base_listboard import BaseListboardView, app_config


class RequisitionModelWrapper(ModelWrapper):

    model_name = app_config.requisition_model
    next_url_name = app_config.requisition_listboard_url_name


class RequisitionListboardView(BaseListboardView):

    navbar_item_selected = 'requisition'

    model_name = app_config.requisition_model
    model_wrapper_class = RequisitionModelWrapper
    listboard_url_name = app_config.requisition_listboard_url_name
    listboard_template_name = app_config.requisition_listboard_template_name
    show_all = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        return {'is_drawn': YES}
