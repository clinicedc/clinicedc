from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY, CLOSED, YES
from django.utils.safestring import mark_safe

from ..constants import (
    ADVERSE_EVENT_ADMIN_SITE,
    ADVERSE_EVENT_APP_LABEL,
    DEATH_REPORT_ACTION,
    DEATH_REPORT_TMG_SECOND_ACTION,
    DEATH_REPORT_TMG_ACTION,
)


class DeathReportTmgAction(ActionWithNotification):
    name = DEATH_REPORT_TMG_ACTION
    display_name = "TMG Death Report (1st) pending"
    notification_display_name = "TMG Death Report (1st)"
    parent_action_names = [DEATH_REPORT_ACTION]
    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreporttmg"
    related_reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreport"
    related_reference_fk_attr = "death_report"
    priority = HIGH_PRIORITY
    create_by_user = False
    color_style = "info"
    show_link_to_changelist = True
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE
    singleton = True
    instructions = mark_safe(f"This report is to be completed by the TMG only.")

    def get_next_actions(self):
        """Returns a second DeathReportTmgAction if the
        submitted TMG report does not match the cause of death
        of the original death report.

        Also, no more than two DeathReportTmgAction can exist.
        """
        next_actions = []
        if not self.matching_cause_of_death:
            next_actions = [DEATH_REPORT_TMG_SECOND_ACTION]
        return next_actions

    def reopen_action_item_on_change(self):
        """Do not reopen if status is CLOSED.
        """
        return self.reference_obj.report_status != CLOSED

    def close_action_item_on_save(self):
        """Close if report status is CLOSED.
        """
        if self.matching_cause_of_death:
            self.delete_children_if_new(parent_action_item=self.action_item)
        return self.reference_obj.report_status == CLOSED

    @property
    def matching_cause_of_death(self):
        """Returns True if cause_of_death_agreed on TMG Death Report is YES.

        Note: the cause of death may be OTHER and the specify
        between death report and TMG different; that is obj.cause_of_death
        match but cause_of_death_agreed is NO.
        """
        return self.reference_obj.cause_of_death_agreed == YES
