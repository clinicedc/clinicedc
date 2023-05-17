from edc_lab.models import Result

from ...model_wrappers import ResultModelWrapper
from .base_listboard_view import BaseListboardView


class ResultListboardView(BaseListboardView):
    form_action_url = "aliquot_form_action_url"
    listboard_template = "result_listboard_template"
    listboard_url = "result_listboard_url"
    listboard_model = Result
    listboard_view_permission_codename = "edc_lab_dashboard.view_lab_result_listboard"
    listboard_view_only_my_permission_codename = None
    model_wrapper_cls = ResultModelWrapper
    navbar_selected_item = "result"
    search_form_url = "result_listboard_url"
