from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY, CLOSED
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from ..constants import (
    DEATH_REPORT_TMG_ACTION,
    DEATH_REPORT_ACTION,
    ADVERSE_EVENT_APP_LABEL,
    ADVERSE_EVENT_ADMIN_SITE,
)


class DeathReportTmgAction(ActionWithNotification):
    name = DEATH_REPORT_TMG_ACTION
    display_name = "TMG Death Report pending"
    notification_display_name = "TMG Death Report"
    parent_action_names = [DEATH_REPORT_ACTION, DEATH_REPORT_TMG_ACTION]
    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreporttmg"
    related_reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreport"
    related_reference_fk_attr = "death_report"
    priority = HIGH_PRIORITY
    create_by_user = False
    color_style = "info"
    show_link_to_changelist = True
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE
    instructions = mark_safe(f"This report is to be completed by the TMG only.")

    def reopen_action_item_on_change(self):
        """Do not reopen if status is CLOSED.
        """
        return self.reference_obj.report_status != CLOSED

    @property
    def matching_cause_of_death(self):
        """Returns True if cause_of_death on TMG Death Report matches
        cause_of_death on Death Report.
        """
        return (
            self.reference_obj.death_report.cause_of_death
            == self.reference_obj.cause_of_death
        )

    def close_action_item_on_save(self):
        if self.matching_cause_of_death:
            self.delete_children_if_new(parent_action_item=self.action_item)
        return self.reference_obj.report_status == CLOSED

    def get_next_actions(self):
        """Returns an second DeathReportTmgAction if the
        submitted report does not match the cause of death
        of the original death report.

        Also, no more than two DeathReportTmgAction can exist.
        """
        next_actions = []
        try:
            self.action_item_model_cls().objects.get(
                parent_action_item=self.related_action_item,
                related_action_item=self.related_action_item,
                action_type__name=self.name,
            )
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            # because more than one action item has the same
            # parent_action_item and related_action_item. this
            # only occurs for older data.
            pass
        else:
            if (
                self.action_item_model_cls()
                .objects.filter(
                    related_action_item=self.related_action_item,
                    action_type__name=self.name,
                )
                .count()
                < 2
            ):
                if (
                    self.reference_obj.cause_of_death
                    != self.related_action_item.reference_obj.cause_of_death
                ):
                    next_actions = ["self"]
        return next_actions
