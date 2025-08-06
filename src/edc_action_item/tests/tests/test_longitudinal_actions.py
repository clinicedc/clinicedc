from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, MALE
from edc_facility import import_holidays
from edc_visit_tracking.constants import SCHEDULED

from edc_action_item import site_action_items
from edc_action_item.models import ActionItem

from ..action_items import CrfLongitudinalOneAction, CrfLongitudinalTwoAction
from ..models import CrfLongitudinalOne
from ..test_case_mixin import TestCaseMixin

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=test_datetime - relativedelta(years=3),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=test_datetime + relativedelta(years=3),
)
class TestLongitudinal(TestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        site_action_items.registry = {}
        site_action_items.register(CrfLongitudinalOneAction)
        site_action_items.register(CrfLongitudinalTwoAction)
        consent_v1 = ConsentDefinition(
            "edc_action_item.subjectconsentv1",
            version="1",
            start=test_datetime,
            end=test_datetime + relativedelta(years=3),
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        self.subject_identifier = self.enroll(consent_datetime=test_datetime, cdef=consent_v1)

    def test_(self):
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        crf_one_a = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_a.action_identifier)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        traveller.stop()
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        crf_one_b = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_b.action_identifier)
        self.assertNotEqual(crf_one_a.action_identifier, crf_one_b.action_identifier)
        traveller.stop()
