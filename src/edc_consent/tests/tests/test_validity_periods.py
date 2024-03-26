from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase, override_settings
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from faker import Faker
from model_bakery import baker

from consent_app.models import SubjectConsent
from edc_consent.site_consents import site_consents

from ..consent_test_utils import consent_factory

fake = Faker()


@time_machine.travel(datetime(2019, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestConsentModel(TestCase):
    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        site_consents.registry = {}
        self.consent_v1 = consent_factory(
            proxy_model="consent_app.subjectconsentv1",
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_v2 = consent_factory(
            proxy_model="consent_app.subjectconsentv2",
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )

        self.consent_v3_start_date = self.study_open_datetime + timedelta(days=101)
        self.consent_v3 = consent_factory(
            proxy_model="consent_app.subjectconsentv3",
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates=self.consent_v2,
        )
        site_consents.register(self.consent_v1)
        site_consents.register(self.consent_v2, updated_by=self.consent_v3)
        site_consents.register(self.consent_v3)
        self.dob = self.study_open_datetime - relativedelta(years=25)

        self.subject_identifier = "123456789"
        self.identity = "987654321"

        # travel to consent v1 validity period and consent subject
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.v1_consent_datetime = get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=self.v1_consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=self.v1_consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        traveller.stop()

        # travel to consent v2 validity period and consent subject
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=51))
        traveller.start()
        self.v2_consent_datetime = get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=self.v2_consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=self.v2_consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        traveller.stop()

        # travel to consent v3 validity period and consent subject
        # not this is 10 days into v3 validity period
        traveller = time_machine.travel(cdef.end + relativedelta(days=10))
        traveller.start()
        self.v3_consent_datetime = get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=self.v3_consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=self.v3_consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        traveller.stop()

        # Note: subject now has three consents in the table.
        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)

    def test_is_v2_within_v2_consent_period(self):
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_v3_start_date - relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "2.0")

    def test_is_v2_after_v2_end_date_but_before_v3_consent_date(self):
        """Assert returns v2 in the gap between the end of the
        v2 consent period and the subject's v3 consent date.
        """
        cdef = site_consents.get_consent_definition(report_datetime=self.v3_consent_datetime)
        SubjectConsent.objects.filter(consent_datetime__range=[cdef.start, cdef.end])

        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=self.v3_consent_datetime - relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "2.0")

    def test_is_v3_on_v3_consent_date(self):
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=self.v3_consent_datetime,
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")

    def test_is_v3_on_after_v3_consent_date(self):
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=self.v3_consent_datetime + relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")
