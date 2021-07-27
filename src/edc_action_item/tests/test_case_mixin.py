from django.test import TestCase
from edc_facility.import_holidays import import_holidays
from edc_metadata.tests.models import SubjectConsent
from edc_reference import ReferenceModelConfig, site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules

from .visit_schedule import visit_schedule


class TestCaseMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @staticmethod
    def enroll(subject_identifier=None):
        subject_identifier = subject_identifier or "1111111"

        site_reference_configs.registry = {}
        reference = ReferenceModelConfig(
            name="edc_action_item.CrfLongitudinalOne", fields=["f1", "f2", "f3"]
        )
        site_reference_configs.register(reference)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )

        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier, consent_datetime=get_utcnow()
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model("edc_metadata.onschedule")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        return subject_identifier

    @staticmethod
    def fake_enroll():
        subject_identifier = "2222222"
        RegisteredSubject.objects.create(subject_identifier=subject_identifier)
        return subject_identifier
