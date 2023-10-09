from __future__ import annotations

from random import choice

from edc_action_item.models import ActionItem
from edc_constants.constants import OTHER, YES
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from model_bakery import baker

from adverse_event_app.visit_schedules import visit_schedule

from ...models import CauseOfDeath


class DeathReportTestMixin:
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        subject_consent = baker.make_recipe(
            "adverse_event_app.subjectconsent", subject_identifier="1234567"
        )
        self.subject_identifier = subject_consent.subject_identifier

        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "adverse_event_app.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

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
            "adverse_event_app.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=YES,
            ae_grade=5,
            user_created="erikvw",
        )

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=ae_initial.action_item,
            reference_model="adverse_event_app.deathreport",
        )

        # create death report
        death_report = baker.make_recipe(
            "adverse_event_app.deathreport",
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=cause_of_death,
            cause_of_death_other=cause_of_death_other,
            user_created="erikvw",
        )
        return death_report
