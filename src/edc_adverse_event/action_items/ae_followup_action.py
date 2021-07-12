from django.conf import settings
from django.utils.safestring import mark_safe
from edc_action_item.action_with_notification import ActionWithNotification
from edc_action_item.site_action_items import site_action_items
from edc_constants.constants import DEAD, HIGH_PRIORITY, YES
from edc_ltfu.constants import LOST_TO_FOLLOWUP
from edc_reportable.constants import GRADE5
from edc_visit_schedule.utils import (
    OnScheduleError,
    get_offschedule_models,
    get_onschedule_models,
)

from edc_adverse_event.constants import (
    AE_FOLLOWUP_ACTION,
    AE_INITIAL_ACTION,
    DEATH_REPORT_ACTION,
)

from ..constants import ADVERSE_EVENT_ADMIN_SITE, ADVERSE_EVENT_APP_LABEL


class AeFollowupAction(ActionWithNotification):

    """
    For example:
        from edc_adverse_event.action_items import AeFollowupAction

        site_action_items.register(AeInitialAction)

    """

    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.aefollowup"
    related_reference_model = f"{ADVERSE_EVENT_APP_LABEL}.aeinitial"

    name = AE_FOLLOWUP_ACTION
    display_name = "Submit AE Followup Report"
    notification_display_name = "AE Followup Report"
    parent_action_names = [AE_INITIAL_ACTION, AE_FOLLOWUP_ACTION]
    related_reference_fk_attr = "ae_initial"
    create_by_user = False
    show_link_to_changelist = True
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE
    instructions = mark_safe(
        f"Upon submission the TMG group will be notified "
        f'by email at <a href="mailto:{settings.EMAIL_CONTACTS.get("tmg") or "#"}">'
        f'{settings.EMAIL_CONTACTS.get("tmg") or "unknown"}</a>'
    )
    priority = HIGH_PRIORITY

    def get_next_actions(self):
        next_actions = []

        # add AE followup to next_actions if followup.
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=self.name,
            required=self.reference_obj.followup == YES,
        )

        # add Death report to next_actions if G5/Death
        next_actions = self.append_to_next_if_required(
            next_actions=next_actions,
            action_name=DEATH_REPORT_ACTION,
            required=(
                self.reference_obj.outcome == DEAD or self.reference_obj.ae_grade == GRADE5
            ),
        )

        next_actions = self.update_next_actions_ltfu(next_actions)
        return next_actions

    @property
    def offschedule_models(self):
        """Returns a list of offschedule models, in label_lower format."""
        return get_offschedule_models(
            subject_identifier=self.subject_identifier,
            report_datetime=self.reference_obj.report_datetime,
        )

    @property
    def onschedule_models(self):
        """Returns a list of offschedule models, in label_lower format."""
        return get_onschedule_models(
            subject_identifier=self.subject_identifier,
            report_datetime=self.reference_obj.report_datetime,
        )

    def update_next_actions_ltfu(self, next_actions=None):
        """Add Study termination to next_actions if LTFU."""
        if self.reference_obj.outcome and self.reference_obj.outcome == LOST_TO_FOLLOWUP:
            if not self.onschedule_models:
                raise OnScheduleError(
                    f"Subject cannot be lost to followup. "
                    f"Subject is not on schedule! Got {self.subject_identifier}."
                )
            for offschedule_model in self.offschedule_models:
                action_cls = site_action_items.get_by_model(model=offschedule_model)
                next_actions = self.append_to_next_if_required(
                    next_actions=next_actions, action_cls=action_cls, required=True
                )
        return next_actions
