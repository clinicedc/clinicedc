from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_facility import import_holidays
from edc_metadata.tests.models import SubjectConsent, SubjectVisit
from edc_reference import ReferenceModelConfig, site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_action_item import site_action_items
from edc_action_item.models import ActionItem
from edc_action_item.tests.visit_schedule import visit_schedule

from ..action_items import CrfLongitudinalOneAction, CrfLongitudinalTwoAction
from ..models import CrfLongitudinalOne


class TestLongitudinal(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        ActionItem.subject_identifier_model = "edc_registration.registeredsubject"
        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(
            name="edc_action_item.CrfLongitudinalOne", fields=["f1", "f2", "f3"]
        )
        site_reference_configs.register(reference)
        site_action_items.registry = {}
        site_action_items.register(CrfLongitudinalOneAction)
        site_action_items.register(CrfLongitudinalTwoAction)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )
        self.subject_identifier = "1111111"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )

        RegisteredSubject.objects.get(subject_identifier=self.subject_identifier)

        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

    def test_(self):
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )
        crf_one_a = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_a.action_identifier)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        crf_one_b = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        crf_one_b.action_identifier
        ActionItem.objects.get(action_identifier=crf_one_b.action_identifier)
        self.assertNotEqual(crf_one_a.action_identifier, crf_one_b.action_identifier)
