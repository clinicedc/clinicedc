from edc_action_item import ActionWithNotification
from edc_adverse_event.constants import DEATH_REPORT_ACTION
from edc_constants.constants import HIGH_PRIORITY
from edc_ltfu.constants import LOSS_TO_FOLLOWUP_ACTION
from edc_prn.constants import UNBLINDING_REVIEW_ACTION

from .constants import END_OF_STUDY_ACTION


class EndOfStudyAction(ActionWithNotification):

    reference_model = None  # "inte_prn.endofstudy"
    admin_site_name = None  # "inte_prn_admin"

    name = END_OF_STUDY_ACTION
    display_name = "Submit End of Study Report"
    notification_display_name = "End of Study Report"
    parent_action_names = [
        UNBLINDING_REVIEW_ACTION,
        DEATH_REPORT_ACTION,
        LOSS_TO_FOLLOWUP_ACTION,
    ]
    show_link_to_changelist = True
    priority = HIGH_PRIORITY
    singleton = True
