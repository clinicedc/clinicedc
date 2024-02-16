from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import time_machine
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_consent.site_consents import site_consents
from edc_facility import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from edc_form_runners.exceptions import FormRunnerModelFormNotFound
from edc_form_runners.form_runner import FormRunner
from edc_form_runners.models import Issue
from form_runners_app.consents import consent_v1
from form_runners_app.models import Member, Team, TeamWithDifferentFields, Venue
from form_runners_app.visit_schedules import visit_schedule


@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
class TestRunners(TestCase):

    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_consents.registry = {}
        site_consents.register(consent_v1)

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}

        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        self.subject_identifier = "1235"
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        self.visit_schedule_name = "visit_schedule"
        self.schedule_name = "schedule"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )

    def test_appointment(self):
        form_runner = FormRunner(model_name="edc_appointment.appointment")
        form_runner.run_all()

    def test_crfs(self):
        for appointment in Appointment.objects.all().order_by("timepoint_datetime"):
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                subject_identifier=self.subject_identifier,
                reason=SCHEDULED,
            )
            TeamWithDifferentFields.objects.create(subject_visit=subject_visit, size=11)
            Venue.objects.create(subject_visit=subject_visit, name=uuid4())
            team = Team.objects.create(subject_visit=subject_visit, name=uuid4())
            Member.objects.create(team=team)
            Member.objects.create(team=team)
            Member.objects.create(team=team)

        # raise on VenueModelAdmin has no custom ModelForm
        self.assertRaises(
            FormRunnerModelFormNotFound, FormRunner, model_name="form_runners_app.venue"
        )

        # run to find name field may not be a UUID
        # see form validator
        form_runner = FormRunner(model_name="form_runners_app.team")
        form_runner.run_all()
        self.assertEqual(Issue.objects.all().count(), 1)
        try:
            Issue.objects.get(
                label_lower="form_runners_app.team",
                visit_code="1000",
                visit_code_sequence=0,
                field_name="name",
                message__icontains="Cannot be a UUID",
            )
        except ObjectDoesNotExist:
            self.fail("Issue model instance unexpectedly does not exist")

        # run to find player_name field may not be a UUID
        # see form validator
        form_runner = FormRunner(model_name="form_runners_app.member")
        form_runner.run_all()
        try:
            Issue.objects.get(
                label_lower="form_runners_app.member",
                visit_code="1000",
                visit_code_sequence=0,
                field_name="player_name",
                message__icontains="Cannot be a UUID",
            )
        except ObjectDoesNotExist:
            self.fail("Issue model instance unexpectedly does not exist")

        # run to assert ignores `name` field because it IS NOT IN admin fieldsets
        # even though the model instance field class has blank=False.
        form_runner = FormRunner(model_name="form_runners_app.teamwithdifferentfields")
        form_runner.run_all()
        try:
            Issue.objects.get(
                label_lower="form_runners_app.teamwithdifferentfields",
                field_name="name",
            )
        except ObjectDoesNotExist:
            pass
        else:
            self.fail("Issue model instance unexpectedly does not exist")
        # assert does not ignore `color` field because it IS IN admin fieldsets
        # and the model instance field class has blank=False.
        try:
            Issue.objects.get(
                label_lower="form_runners_app.teamwithdifferentfields",
                field_name="color",
            )
        except ObjectDoesNotExist:
            self.fail("Issue model instance unexpectedly does not exist")
