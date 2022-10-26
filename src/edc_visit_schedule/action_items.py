from edc_action_item import ActionWithNotification
from edc_adverse_event.constants import DEATH_REPORT_ACTION
from edc_constants.constants import HIGH_PRIORITY
from edc_ltfu.constants import LTFU_ACTION
from edc_offstudy.constants import END_OF_STUDY_ACTION

from .constants import OFFSCHEDULE_ACTION


class OffscheduleAction(ActionWithNotification):
    name = OFFSCHEDULE_ACTION
    display_name = "Submit Off-Schedule"
    notification_display_name = "Off-Schedule"
    parent_action_names = [
        DEATH_REPORT_ACTION,
        LTFU_ACTION,
    ]
    reference_model = "intecomm_prn.offschedule"
    show_link_to_changelist = True
    admin_site_name = "intecomm_prn_admin"
    priority = HIGH_PRIORITY
    singleton = True

    def get_next_actions(self):
        return [END_OF_STUDY_ACTION]
