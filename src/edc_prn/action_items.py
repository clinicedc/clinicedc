from edc_action_item import ActionWithNotification
from edc_constants.constants import CLOSED, HIGH_PRIORITY

from .constants import PROTOCOL_DEVIATION_VIOLATION_ACTION


class ProtocolDeviationViolationAction(ActionWithNotification):
    name = PROTOCOL_DEVIATION_VIOLATION_ACTION
    display_name = "Submit Protocol Deviation/Violation Report"
    notification_display_name = "Protocol Deviation/Violation Report"
    parent_action_names = []
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY

    reference_model = None  # "ambition_prn.protocoldeviationviolation"
    admin_site_name = None  # "ambition_prn_admin"

    def close_action_item_on_save(self):
        return self.reference_obj.report_status == CLOSED
