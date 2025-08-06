from edc_action_item import ActionWithNotification
from edc_constants.constants import CLOSED, HIGH_PRIORITY

from .constants import (
    PROTOCOL_DEVIATION_VIOLATION_ACTION,
    PROTOCOL_INCIDENT_ACTION,
    WITHDRAWN,
)


class ProtocolDeviationViolationAction(ActionWithNotification):
    reference_model = None  # "my_app.protocolincident"
    admin_site_name = None  # "my_app_admin"

    name = PROTOCOL_DEVIATION_VIOLATION_ACTION
    display_name = "Submit Protocol Deviation / Violation Report"
    notification_display_name = "Protocol Deviation / Violation Report"
    parent_action_names = []
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY

    def close_action_item_on_save(self):
        return self.reference_obj.report_status == CLOSED


class ProtocolIncidentAction(ActionWithNotification):
    reference_model = None  # "my_app.protocolincident"
    admin_site_name = None  # "my_app"

    name = PROTOCOL_INCIDENT_ACTION
    display_name = "Submit Protocol Incident Report"
    notification_display_name = "Protocol Incident Report"
    parent_action_names = []
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY

    def close_action_item_on_save(self):
        return self.reference_obj.report_status in [CLOSED, WITHDRAWN]
