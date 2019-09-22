from django.apps import apps as django_apps
from edc_action_item import ActionWithNotification
from edc_adverse_event.constants import (
    AE_INITIAL_ACTION,
    AE_FOLLOWUP_ACTION,
    DEATH_REPORT_ACTION,
)
from edc_constants.constants import HIGH_PRIORITY

from ..constants import ADVERSE_EVENT_ADMIN_SITE, ADVERSE_EVENT_APP_LABEL
from django.core.exceptions import ObjectDoesNotExist
from edc_visit_schedule.utils import get_offschedule_models


class DeathReportAction(ActionWithNotification):
    name = DEATH_REPORT_ACTION
    display_name = "Submit Death Report"
    notification_display_name = "Death Report"
    reference_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreport"
    death_report_tmg_model = f"{ADVERSE_EVENT_APP_LABEL}.deathreporttmg"
    parent_action_names = [AE_INITIAL_ACTION, AE_FOLLOWUP_ACTION]
    show_link_to_changelist = True
    show_link_to_add = True
    admin_site_name = ADVERSE_EVENT_ADMIN_SITE
    priority = HIGH_PRIORITY
    singleton = True
    dirty_fields = ["cause_of_death"]

    def get_next_actions(self):
        """Adds 1 DEATHReportTMG if not yet created and
        STUDY_TERMINATION_CONCLUSION if required.
        """
        next_actions = []
        next_actions = self.append_next_death_tmg_action(next_actions)
        next_actions = self.append_next_study_termination_action(next_actions)
        return next_actions

    def append_next_death_tmg_action(self, next_actions):
        # DEATH_REPORT_TMG_ACTION
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
        # STUDY_TERMINATION_CONCLUSION_ACTION
        for off_schedule_model in get_offschedule_models().values():
            off_schedule_cls = django_apps.get_model(off_schedule_model)
            try:
                off_schedule_cls.objects.get(subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                next_actions.append(off_schedule_cls.action_name)
        return next_actions
