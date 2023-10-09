from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_action_item import site_action_items
from edc_consent import site_consents
from edc_consent.tests.consent_test_utils import consent_object_factory
from edc_facility.import_holidays import import_holidays
from edc_lab import site_labs
from edc_metadata.tests.models import SubjectConsent
from edc_reference import site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_reportable import site_reportables
from edc_reportable.grading_data.daids_july_2017 import grading_data
from edc_reportable.normal_data.africa import normal_data
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_lab_results.action_items import register_actions

from .lab_profiles import subject_lab_profile
from .visit_schedule import visit_schedule


class TestCaseMixin(TestCase):
    @classmethod
    def setUpClass(cls):
        site_reportables._registry = {}
        site_labs.initialize()
        site_action_items.registry = {}
        site_reference_configs.registry = {}
        site_visit_schedules._registry = {}
        site_consents.registry = {}
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        site_visit_schedules.register(visit_schedule)
        consent_object_factory(
            model=SubjectConsent._meta.label_lower,
            start=get_utcnow() - relativedelta(years=1),
            end=get_utcnow() + relativedelta(years=1),
        )
        import_holidays()
        site_reportables.register(
            name="my_reportables", normal_data=normal_data, grading_data=grading_data
        )
        site_labs.register(lab_profile=subject_lab_profile)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )
        register_actions()

    @staticmethod
    def enroll(subject_identifier=None):
        subject_identifier = subject_identifier or "1111111"
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
