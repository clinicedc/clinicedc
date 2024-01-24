from typing import Type

from django.apps import apps as django_apps
from django.test import TestCase
from edc_action_item import site_action_items
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_reportable import site_reportables
from edc_reportable.grading_data.daids_july_2017 import grading_data
from edc_reportable.normal_data.africa import normal_data
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit_schedule import VisitSchedule
from edc_visit_tracking.constants import SCHEDULED

from edc_utils import get_utcnow


class LongitudinalTestCaseMixin(TestCase):
    consent_definition: ConsentDefinition = None
    visit_schedule: VisitSchedule = None
    helper_cls: Type[Helper] = Helper

    @classmethod
    def setUpClass(cls):
        site_reportables._registry = {}
        site_action_items.registry = {}
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        site_reportables.register(
            name="my_reportables", normal_data=normal_data, grading_data=grading_data
        )
        site_consents.registry = {}
        site_consents.register(cls.consent_definition)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=cls.visit_schedule)
        import_holidays()

    def enroll(self, subject_identifier=None):
        subject_identifier = subject_identifier or "1111111"
        self.helper = self.helper_cls(
            subject_identifier=subject_identifier,
        )
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        return subject_identifier

    @staticmethod
    def fake_enroll():
        subject_identifier = "2222222"
        RegisteredSubject.objects.create(subject_identifier=subject_identifier)
        return subject_identifier

    def create_visits(self, subject_identifier):
        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code="1000",
            visit_code_sequence=0,
        )
        self.subject_visit_baseline = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
            visit_code="1000",
            visit_code_sequence=0,
        )

        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code="2000",
            visit_code_sequence=0,
        )
        self.subject_visit_followup = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
            visit_code="4000",
            visit_code_sequence=0,
        )
