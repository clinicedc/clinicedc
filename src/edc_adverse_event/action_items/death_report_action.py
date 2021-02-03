from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_action_item import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY
from edc_visit_schedule.utils import get_offschedule_models

from edc_adverse_event.constants import (
    AE_FOLLOWUP_ACTION,
    AE_INITIAL_ACTION,
    DEATH_REPORT_ACTION,
)

from ..constants import ADVERSE_EVENT_ADMIN_SITE, ADVERSE_EVENT_APP_LABEL


class DeathReportAction(ActionWithNotification):
    name = DEATH_REPORT_ACTION
    display_name = "Submit Death Report"
    notification_display_name = "Death Report"
    parent_action_names = [AE_INITIAL_ACTION, AE_FOLLOWUP_ACTION]
    show_link_to_changelist = True
    show_link_to_add = True
    priority = HIGH_PRIORITY
    singleton = True
    dirty_fields = ["cause_of_death"]
    enable_tmg_workflow = True

    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreport"
    death_report_tmg_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreporttmg"
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE

    def get_next_actions(self):
        """Adds 1 DEATHReportTMG if not yet created and
        STUDY_TERMINATION_CONCLUSION if required.
        """
        next_actions = []
        if self.enable_tmg_workflow:
            next_actions = self.append_next_death_tmg_action(next_actions)
        next_actions = self.append_next_off_schedule_action(next_actions)
        return next_actions

    def append_next_death_tmg_action(self, next_actions):
        if self.death_report_tmg_model:
            tmg_model_cls = django_apps.get_model(self.death_report_tmg_model)
            try:
                self.action_item_model_cls().objects.get(
                    parent_action_item=self.reference_obj.action_item,
                    related_action_item=self.reference_obj.action_item,
                    action_type__name=tmg_model_cls.action_name,
                )
            except ObjectDoesNotExist:
                next_actions = [tmg_model_cls.action_name]
        return next_actions

    def append_next_off_schedule_action(self, next_actions):
        """Appends an off schedule action to the list for each
        schedule the subject is on.

        If subject was already taken off schedule, skip. For example,
        if re-saving the DeathReport, subject may have already been
        taken off schedule.
        """
        offschedule_models = get_offschedule_models(
            subject_identifier=self.subject_identifier,
            report_datetime=self.reference_obj.report_datetime,
        )
        for off_schedule_model in offschedule_models:
            off_schedule_cls = django_apps.get_model(off_schedule_model)
            try:
                off_schedule_cls.objects.get(subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                next_actions.append(off_schedule_cls.action_name)
        return next_actions
