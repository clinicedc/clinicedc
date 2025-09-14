from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY
from edc_offstudy.constants import END_OF_STUDY_ACTION
from edc_visit_tracking.constants import VISIT_MISSED_ACTION

from .constants import LTFU_ACTION
from .utils import get_ltfu_model_name


class LtfuAction(ActionWithNotification):
    reference_model = get_ltfu_model_name()
    admin_site_name = "edc_ltfu_admin"

    name = LTFU_ACTION
    display_name = "Submit Loss to Follow Up Report"
    notification_display_name = "Loss to Follow Up Report"
    parent_action_names = (VISIT_MISSED_ACTION,)
    show_link_to_changelist = True
    priority = HIGH_PRIORITY

    def get_next_actions(self):
        next_actions = [END_OF_STUDY_ACTION]
        return next_actions
