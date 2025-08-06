from edc_constants.constants import CLOSED, NEW, OPEN

from ...view_mixins import StatusTmgAeListboardView


class NewTmgAeListboardView(StatusTmgAeListboardView):
    listboard_url = "new_tmg_ae_listboard_url"
    search_form_url = "new_tmg_ae_listboard_url"
    status = NEW
    listboard_panel_title = "TMG AE Reports: New"


class OpenTmgAeListboardView(StatusTmgAeListboardView):
    listboard_url = "open_tmg_ae_listboard_url"
    search_form_url = "open_tmg_ae_listboard_url"
    status = OPEN
    listboard_panel_title = "TMG AE Reports: Open"


class ClosedTmgAeListboardView(StatusTmgAeListboardView):
    listboard_url = "closed_tmg_ae_listboard_url"
    search_form_url = "closed_tmg_ae_listboard_url"
    status = CLOSED
    listboard_panel_title = "TMG AE Reports: Closed"
