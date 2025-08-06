from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .consents import consent_v1
from .visit_schedule import get_visit_schedule


class TestCaseMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @staticmethod
    def enroll(
        subject_identifier=None,
        site_id: int | None = None,
        consent_datetime: datetime | None = None,
        cdef: ConsentDefinition | None = None,
    ):
        subject_identifier = subject_identifier or "1111111"

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(cdef or consent_v1))

        site_consents.registry = {}
        site_consents.register(cdef or consent_v1)
        consent_datetime = consent_datetime or get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        subject_consent = cdef.model_cls.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            dob=consent_datetime - relativedelta(years=25),
            site_id=site_id or settings.SITE_ID,
        )
        RegisteredSubject.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            site_id=site_id or settings.SITE_ID,
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        schedule.put_on_schedule(
            subject_consent.subject_identifier,
            subject_consent.consent_datetime,
            skip_get_current_site=True,
        )
        return subject_identifier

    @staticmethod
    def fake_enroll(subject_identifier: str | None = None, site_id: int | None = None):
        subject_identifier = subject_identifier or "2222222"
        RegisteredSubject.objects.create(
            subject_identifier=subject_identifier, site_id=site_id
        )
        return subject_identifier
