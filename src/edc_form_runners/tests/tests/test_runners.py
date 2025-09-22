from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import Member, Team, TeamWithDifferentFields, Venue
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule_form_runners.visit_schedule import (
    get_visit_schedule,
)
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag

from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_form_runners.exceptions import FormRunnerModelFormNotFound
from edc_form_runners.form_runner import FormRunner
from edc_form_runners.models import Issue
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.models import SubjectVisit


@tag("form_runners")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
class TestRunners(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        sites._registry = {}
        sites.loaded = False
        sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}

        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        self.visit_schedule_name = "visit_schedule"
        self.schedule_name = "schedule"

        subject_consent = helper.enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = subject_consent.subject_identifier

    def test_appointment(self):
        form_runner = FormRunner(model_name="edc_appointment.appointment")
        form_runner.run_all()

    def test_crfs(self):
        for appointment in Appointment.objects.all().order_by("timepoint_datetime"):
            subject_visit = SubjectVisit.objects.get(appointment=appointment)
            TeamWithDifferentFields.objects.create(subject_visit=subject_visit, size=11)
            Venue.objects.create(subject_visit=subject_visit, name=uuid4())
            team = Team.objects.create(subject_visit=subject_visit, name=uuid4())
            Member.objects.create(team=team)
            Member.objects.create(team=team)
            Member.objects.create(team=team)

        # raise on VenueModelAdmin has no custom ModelForm
        self.assertRaises(
            FormRunnerModelFormNotFound, FormRunner, model_name="clinicedc_tests.venue"
        )

        # run to find `name` field may not be a UUID
        # see form validator
        form_runner = FormRunner(model_name="clinicedc_tests.team")
        form_runner.run_all()
        self.assertEqual(Issue.objects.all().count(), 1)
        try:
            Issue.objects.get(
                label_lower="clinicedc_tests.team",
                visit_code="1000",
                visit_code_sequence=0,
                field_name="name",
                message__icontains="Cannot be a UUID",
            )
        except ObjectDoesNotExist:
            self.fail("Issue model instance unexpectedly does not exist")

        # run to find `player_name` field may not be a UUID
        # see form validator
        form_runner = FormRunner(model_name="clinicedc_tests.member")
        form_runner.run_all()
        try:
            Issue.objects.get(
                label_lower="clinicedc_tests.member",
                visit_code="1000",
                visit_code_sequence=0,
                field_name="player_name",
                message__icontains="Cannot be a UUID",
            )
        except ObjectDoesNotExist:
            self.fail("Issue model instance unexpectedly does not exist")

        # run to assert ignores `name` field because it IS NOT IN admin fieldsets
        # even though the model instance field class has blank=False.
        form_runner = FormRunner(model_name="clinicedc_tests.teamwithdifferentfields")
        form_runner.run_all()
        try:
            Issue.objects.get(
                label_lower="clinicedc_tests.teamwithdifferentfields",
                field_name="name",
            )
        except ObjectDoesNotExist:
            pass
        else:
            self.fail("Issue model instance unexpectedly exists")
        # assert does not ignore `color` field because it IS IN admin fieldsets
        # and the model instance field class has blank=False.
        try:
            Issue.objects.get(
                label_lower="clinicedc_tests.teamwithdifferentfields",
                field_name="color",
            )
        except ObjectDoesNotExist:
            self.fail("Issue model instance unexpectedly does not exist")
