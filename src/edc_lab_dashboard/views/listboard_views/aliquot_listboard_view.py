from edc_lab.models import Aliquot

from ...model_wrappers import AliquotModelWrapper
from ..listboard_filters import AliquotListboardViewFilters
from .base_listboard_view import BaseListboardView


class AliquotListboardView(BaseListboardView):

    form_action_url = "aliquot_form_action_url"
    listboard_template = "aliquot_listboard_template"
    listboard_url = "aliquot_listboard_url"
    listboard_view_filters = AliquotListboardViewFilters()
    listboard_view_permission_codename = "edc_dashboard.view_lab_aliquot_listboard"
    listboard_view_only_my_permission_codename = None
    listboard_model = Aliquot
    model_wrapper_cls = AliquotModelWrapper
    navbar_selected_item = "aliquot"
    search_form_url = "aliquot_listboard_url"
    show_all = True
