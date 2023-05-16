from edc_action_item import ActionWithNotification
from edc_constants.constants import DEAD, HIGH_PRIORITY, NO, YES
from edc_reportable import GRADE3, GRADE4, GRADE5

from edc_adverse_event.constants import (
    AE_FOLLOWUP_ACTION,
    AE_INITIAL_ACTION,
    AE_SUSAR_ACTION,
    AE_TMG_ACTION,
    DEATH_REPORT_ACTION,
)

from ..constants import ADVERSE_EVENT_ADMIN_SITE, ADVERSE_EVENT_APP_LABEL


class AeInitialAction(ActionWithNotification):
    name = AE_INITIAL_ACTION
    display_name = "Submit AE Initial Report"
    notification_display_name = "AE Initial Report"
    parent_action_names = []
    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.aeinitial"
    show_link_to_changelist = True
    show_link_to_add = True
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE
    instructions = "Complete the initial AE report"
    priority = HIGH_PRIORITY

    @property
    def deceased(self):
        if (self.reference_obj.ae_grade and self.reference_obj.ae_grade == GRADE5) or (
            self.reference_obj.sae_reason.name and self.reference_obj.sae_reason.name == DEAD
        ):
            return True
        return False

    def get_next_actions(self):
        """Returns next actions."""
        next_actions = []
        next_actions = self.append_ae_followup_next_action(next_actions)
        next_actions = self.append_ae_susar_next_action(next_actions)
        next_actions = self.append_ae_tmg_next_action(next_actions)
        next_actions = self.append_death_report_next_action(next_actions)
        return next_actions

    def append_ae_susar_next_action(self, next_actions=None):
        """Add next AE_SUSAR_ACTION if SUSAR == YES."""
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=AE_SUSAR_ACTION,
            required=(
                self.reference_obj.susar == YES and self.reference_obj.susar_reported == NO
            ),
        )
        return next_actions

    def append_ae_followup_next_action(self, next_actions=None):
        """Add next AeFollowup if not deceased."""
        if not self.deceased:
            next_actions = self.append_to_next_if_required(
                action_name=AE_FOLLOWUP_ACTION, next_actions=next_actions
            )
        return next_actions

    def append_ae_tmg_next_action(self, next_actions=None):
        """add next AE Tmg if G3+SAE, G4, or G5/Death."""
        # add next AeTmgAction if G5/Death
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions, action_name=AE_TMG_ACTION, required=self.deceased
        )
        # add next AeTmgAction if G4
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=AE_TMG_ACTION,
            required=self.reference_obj.ae_grade == GRADE4,
        )
        # add next AeTmgAction if G3 and is an SAE
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=AE_TMG_ACTION,
            required=(self.reference_obj.ae_grade == GRADE3 and self.reference_obj.sae == YES),
        )
        return next_actions

    def append_death_report_next_action(self, next_actions=None):
        """Add next Death report if G5/Death."""
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=DEATH_REPORT_ACTION,
            required=self.deceased,
        )
        return next_actions
