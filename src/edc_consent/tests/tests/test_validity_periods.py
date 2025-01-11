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

from ...consent_definition import ConsentDefinition
from ...exceptions import ConsentDefinitionDoesNotExist
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
        self.register_with_site_consents()
        self.dob = self.study_open_datetime - relativedelta(years=25)

        self.subject_identifier = "123456789"
        self.identity = "987654321"

    def register_with_site_consents(
        self,
        consent_v1: ConsentDefinition | None = None,
        consent_v2: ConsentDefinition | None = None,
        consent_v3: ConsentDefinition | None = None,
    ) -> tuple[ConsentDefinition, ConsentDefinition, ConsentDefinition]:
        site_consents.registry = {}
        if consent_v1 is None:
            consent_v1 = consent_factory(
                proxy_model="consent_app.subjectconsentv1",
                start=self.study_open_datetime,
                end=self.study_open_datetime + timedelta(days=50),
                version="1.0",
            )
        if consent_v2 is None:
            consent_v2 = consent_factory(
                proxy_model="consent_app.subjectconsentv2",
                start=self.study_open_datetime + timedelta(days=51),
                end=self.study_open_datetime + timedelta(days=100),
                version="2.0",
            )

        if consent_v3 is None:
            self.consent_v3_start_date = self.study_open_datetime + timedelta(days=101)
            consent_v3 = consent_factory(
                proxy_model="consent_app.subjectconsentv3",
                start=self.study_open_datetime + timedelta(days=101),
                end=self.study_open_datetime + timedelta(days=150),
                version="3.0",
                updates=consent_v2,
            )
        site_consents.register(consent_v1)
        site_consents.register(consent_v2, updated_by=consent_v3)
        site_consents.register(consent_v3)
        return consent_v1, consent_v2, consent_v3

    def create_v1_consent_for_subject(self) -> datetime:
        # travel to consent v1 validity period and consent subject
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        consent_datetime = get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        traveller.stop()
        return consent_datetime

    def create_v2_consent_for_subject(self) -> datetime:
        # travel to consent v2 validity period and consent subject
        traveller = time_machine.travel(self.study_open_datetime + timedelta(days=51))
        traveller.start()
        consent_datetime = get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        traveller.stop()
        return consent_datetime

    def create_v3_consent_for_subject(self, days: int | None = None) -> datetime:
        """Use a consent datetime relative to the version 2 end date."""
        # travel to consent v3 validity period and consent subject
        days = days or 10
        cdef_v2 = site_consents.get_consent_definition(version="2.0")
        cdef = site_consents.get_consent_definition(report_datetime=cdef_v2.start)
        traveller = time_machine.travel(cdef.end + relativedelta(days=days))
        traveller.start()
        consent_datetime = get_utcnow()  # cdef.enf + xx days
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=get_utcnow() - relativedelta(years=25),
        )
        traveller.stop()
        return consent_datetime

    def test_is_v2_within_v2_consent_period(self):
        consent_v1, consent_v2, consent_v3 = self.register_with_site_consents()
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        self.create_v3_consent_for_subject()

        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)

        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=consent_v3.start - relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "2.0")

    def test_consent_date_is_for_version(self):
        """There should be no-gap! If they haven't signed V3 then
        data entry must stop unless there is overlap. In the case
        of overlap. the higher version consent should be used.
        """
        self.register_with_site_consents()
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        v3_consent_datetime = self.create_v3_consent_for_subject(days=10)

        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)
        cdef = site_consents.get_consent_definition(report_datetime=v3_consent_datetime)
        cosent_obj_v3 = SubjectConsent.objects.get(
            consent_datetime__range=[cdef.start, cdef.end]
        )
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=cosent_obj_v3.consent_datetime - relativedelta(days=6),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=cosent_obj_v3.consent_datetime - relativedelta(days=11),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "2.0")

    def test_v3_consent_date_gap(self):
        """Assert raises if no consent definition covers the intended
        consent date.
        """
        consent_v2 = consent_factory(
            proxy_model="consent_app.subjectconsentv2",
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )
        consent_v3 = consent_factory(
            proxy_model="consent_app.subjectconsentv3",
            start=self.study_open_datetime + timedelta(days=120),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates=consent_v2,
        )
        self.register_with_site_consents(consent_v2=consent_v2, consent_v3=consent_v3)

        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        # cannot consent, date does not fall within a consent period
        self.assertRaises(
            ConsentDefinitionDoesNotExist, self.create_v3_consent_for_subject, days=10
        )

        # ok, date does falls within a consent period
        self.create_v3_consent_for_subject(days=30)

    def test_is_v3_on_v3_consent_date(self):
        self.register_with_site_consents()
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        v3_consent_datetime = self.create_v3_consent_for_subject()

        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)

        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=v3_consent_datetime,
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")

    def test_is_v3_on_after_v3_consent_date(self):
        self.register_with_site_consents()
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        v3_consent_datetime = self.create_v3_consent_for_subject()

        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)

        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=v3_consent_datetime + relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")
