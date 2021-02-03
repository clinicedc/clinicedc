from django.utils.safestring import mark_safe
from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import CLOSED, HIGH_PRIORITY

from ..constants import (
    ADVERSE_EVENT_ADMIN_SITE,
    ADVERSE_EVENT_APP_LABEL,
    DEATH_REPORT_TMG_ACTION,
    DEATH_REPORT_TMG_SECOND_ACTION,
)


class DeathReportTmgSecondAction(ActionWithNotification):
    name = DEATH_REPORT_TMG_SECOND_ACTION
    display_name = "TMG Death Report (2nd) pending"
    notification_display_name = "TMG Death Report (2nd)"
    parent_action_names = [DEATH_REPORT_TMG_ACTION]
    related_reference_fk_attr = "death_report"
    priority = HIGH_PRIORITY
    create_by_user = False
    color_style = "info"
    show_link_to_changelist = True
    singleton = True
    instructions = mark_safe("This report is to be completed by the TMG only.")

    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreporttmgsecond"
    related_reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreport"
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE

    def close_and_create_next(self):
        super().close_and_create_next()

    def reopen_action_item_on_change(self):
        """Do not reopen if report status is CLOSED."""
        return self.reference_obj.report_status != CLOSED

    def close_action_item_on_save(self):
        """Close if report status is CLOSED."""
        return self.reference_obj.report_status == CLOSED
