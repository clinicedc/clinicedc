from django.utils.safestring import mark_safe
from edc_action_item import ActionWithNotification
from edc_constants.constants import CLOSED, HIGH_PRIORITY

from edc_adverse_event.constants import (
    AE_FOLLOWUP_ACTION,
    AE_INITIAL_ACTION,
    AE_TMG_ACTION,
)

from ..constants import ADVERSE_EVENT_ADMIN_SITE, ADVERSE_EVENT_APP_LABEL


class AeTmgAction(ActionWithNotification):
    name = AE_TMG_ACTION
    display_name = "TMG AE Report pending"
    notification_display_name = "TMG AE Report"
    parent_action_names = [AE_INITIAL_ACTION, AE_FOLLOWUP_ACTION, AE_TMG_ACTION]
    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.aetmg"
    related_reference_model = f"{ADVERSE_EVENT_APP_LABEL}.aeinitial"
    related_reference_fk_attr = "ae_initial"
    create_by_user = False
    color_style = "info"
    show_link_to_changelist = True
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE
    instructions = mark_safe("This report is to be completed by the TMG only.")
    priority = HIGH_PRIORITY

    def close_action_item_on_save(self):
        return self.reference_obj.report_status == CLOSED
