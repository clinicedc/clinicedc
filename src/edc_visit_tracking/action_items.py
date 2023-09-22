from typing import List

from edc_action_item import Action
from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY, YES
from edc_ltfu.constants import LTFU_ACTION

from .constants import VISIT_MISSED_ACTION


class VisitMissedAction(ActionWithNotification):
    name: str = VISIT_MISSED_ACTION
    display_name: str = "Submit Missed Visit"
    notification_display_name: str = " Submit Missed Visit"
    parent_action_names: List[str] = []
    show_link_to_changelist: bool = True
    priority: str = HIGH_PRIORITY
    loss_to_followup_action_name: str = LTFU_ACTION

    reference_model: str = None  # "inte_subject.subjectvisitmissed"
    admin_site_name: str = None  # "inte_prn_admin"

    def get_loss_to_followup_action_name(self) -> str:
        return self.loss_to_followup_action_name

    def is_ltfu(self) -> bool:
        return self.reference_obj.ltfu == YES

    def get_next_actions(self) -> List[Action]:
        next_actions: List[Action] = []
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=self.get_loss_to_followup_action_name(),
            required=self.is_ltfu(),
        )
        return next_actions


class MissedVisitAction(VisitMissedAction):
    pass
