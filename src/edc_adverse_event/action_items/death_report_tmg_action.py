from django.utils.safestring import mark_safe
from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import CLOSED, HIGH_PRIORITY, NO, YES

from ..constants import (
    ADVERSE_EVENT_ADMIN_SITE,
    ADVERSE_EVENT_APP_LABEL,
    DEATH_REPORT_ACTION,
    DEATH_REPORT_TMG_ACTION,
    DEATH_REPORT_TMG_SECOND_ACTION,
)


class DeathReportTmgAction(ActionWithNotification):
    name = DEATH_REPORT_TMG_ACTION
    display_name = "TMG Death Report (1st) pending"
    notification_display_name = "TMG Death Report (1st)"
    parent_action_names = [DEATH_REPORT_ACTION]
    related_reference_fk_attr = "death_report"
    priority = HIGH_PRIORITY
    create_by_user = False
    color_style = "info"
    show_link_to_changelist = True
    singleton = True
    instructions = mark_safe("This report is to be completed by the TMG only.")

    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreporttmg"
    related_reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreport"
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE

    def get_next_actions(self):
        """Returns a DeathReportTmgSecondAction if the
        submitted TMG report does not match the cause of death
        of the original death report.
        """
        next_actions = []
        if self.reference_obj.cause_of_death_agreed == NO:
            next_actions = [DEATH_REPORT_TMG_SECOND_ACTION]
        return next_actions

    def reopen_action_item_on_change(self):
        """Do not reopen if status is CLOSED."""
        return self.reference_obj.report_status != CLOSED

    def close_action_item_on_save(self):
        """Close if report status is CLOSED."""
        if self.reference_obj.cause_of_death_agreed == YES:
            self.delete_children_if_new(parent_action_item=self.action_item)
        return self.reference_obj.report_status == CLOSED
