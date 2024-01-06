from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .visit_schedule import visit_schedule


class TestCaseMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @staticmethod
    def enroll(subject_identifier=None):
        subject_identifier = subject_identifier or "1111111"

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        consent_datetime = get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        subject_consent = cdef.model_cls.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        RegisteredSubject.objects.create(subject_identifier=subject_identifier)
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
