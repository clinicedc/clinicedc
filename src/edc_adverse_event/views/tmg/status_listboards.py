from edc_constants.constants import CLOSED, NEW, OPEN

from ...model_wrappers import (
    ClosedTmgActionItemModelWrapper,
    NewTmgActionItemModelWrapper,
    OpenTmgActionItemModelWrapper,
)
from ...view_mixins import StatusTmgAeListboardView


class NewTmgAeListboardView(StatusTmgAeListboardView):

    listboard_url = "new_tmg_ae_listboard_url"
    search_form_url = "new_tmg_ae_listboard_url"
    status = NEW
    listboard_panel_title = "TMG: New AE Reports"
    model_wrapper_cls = NewTmgActionItemModelWrapper


class OpenTmgAeListboardView(StatusTmgAeListboardView):

    listboard_url = "open_tmg_ae_listboard_url"
    search_form_url = "open_tmg_ae_listboard_url"
    status = OPEN
    listboard_panel_title = "TMG: Open AE Reports"
    model_wrapper_cls = OpenTmgActionItemModelWrapper


class ClosedTmgAeListboardView(StatusTmgAeListboardView):

    listboard_url = "closed_tmg_ae_listboard_url"
    search_form_url = "closed_tmg_ae_listboard_url"
    status = CLOSED
    listboard_panel_title = "TMG: Closed AE Reports"
    model_wrapper_cls = ClosedTmgActionItemModelWrapper
