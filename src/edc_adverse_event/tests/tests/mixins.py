from __future__ import annotations

from random import choice

from model_bakery import baker

from edc_action_item.models import ActionItem
from edc_adverse_event.models import CauseOfDeath
from edc_consent import site_consents
from edc_constants.constants import OTHER, YES
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from tests.action_items import register_actions
from tests.consents import consent_v1
from tests.helper import Helper
from tests.visit_schedules.visit_schedule import get_visit_schedule


class DeathReportTestMixin:
    helper_cls = Helper

    def setUp(self):
        register_actions()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        helper = self.helper_cls()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            consent_definition=consent_v1,
        )
        self.subject_identifier = subject_consent.subject_identifier

    def get_death_report(
        self,
        cause_of_death: str | None = None,
        cause_of_death_other: str | None = None,
    ):
        causes_qs = CauseOfDeath.objects.exclude(name=OTHER)
        cause_of_death = (
            cause_of_death
            or causes_qs[choice([x for x in range(0, len(causes_qs))])]  # nosec B311
        )

        # create ae initial
        ae_initial = baker.make_recipe(
            "tests.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=YES,
            ae_grade=5,
            user_created="erikvw",
        )

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=ae_initial.action_item,
            action_type__reference_model="tests.deathreport",
        )

        # create death report
        death_report = baker.make_recipe(
            "tests.deathreport",
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=cause_of_death,
            cause_of_death_other=cause_of_death_other,
            user_created="erikvw",
        )
        return death_report
