from edc_action_item.action import Action
from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY, YES
from edc_ltfu.constants import LTFU_ACTION

from .constants import VISIT_MISSED_ACTION


class VisitMissedAction(ActionWithNotification):
    name = VISIT_MISSED_ACTION
    display_name = "Submit Missed Visit"
    notification_display_name = " Submit Missed Visit"
    parent_action_names = ()
    show_link_to_changelist = True
    priority = HIGH_PRIORITY
    loss_to_followup_action_name = LTFU_ACTION

    reference_model = None  # "inte_subject.subjectvisitmissed"
    admin_site_name = None  # "inte_prn_admin"

    def get_loss_to_followup_action_name(self) -> str:
        return self.loss_to_followup_action_name

    def is_ltfu(self) -> bool:
        return self.reference_obj.ltfu == YES

    def get_next_actions(self) -> list[Action]:
        next_actions: list[Action] = []
        return self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=self.get_loss_to_followup_action_name(),
            required=self.is_ltfu(),
        )


class MissedVisitAction(VisitMissedAction):
    pass
