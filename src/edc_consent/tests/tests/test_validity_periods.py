from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent1_v1, consent1_v2, consent1_v3
from clinicedc_tests.models import SubjectConsent
from clinicedc_tests.sites import all_sites
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase, override_settings, tag
from django.utils import timezone
from faker import Faker
from model_bakery import baker

from edc_consent.exceptions import ConsentDefinitionDoesNotExist
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites

from ..consent_test_utils import consent_factory

fake = Faker()


@tag("consent")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(EDC_AUTH_SKIP_SITE_AUTHS=True, EDC_AUTH_SKIP_AUTH_UPDATER=False, SITE_ID=10)
class TestConsentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        site_consents.registry = {}
        site_consents.register(consent1_v1)
        site_consents.register(consent1_v2, updated_by=consent1_v3)
        site_consents.register(consent1_v3)
        self.dob = self.study_open_datetime - relativedelta(years=25)

        self.subject_identifier = "123456789"
        self.identity = "987654321"

    def create_v1_consent_for_subject(
        self, travel_datetime: datetime | None = None
    ) -> datetime:
        # travel to consent v1 validity period and consent subject
        traveller = time_machine.travel(travel_datetime or self.study_open_datetime)
        traveller.start()
        consent_datetime = timezone.now()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=timezone.now() - relativedelta(years=25),
        )
        traveller.stop()
        return consent_datetime

    def create_v2_consent_for_subject(
        self, travel_datetime: datetime | None = None
    ) -> datetime:
        # travel to consent v2 validity period and consent subject
        traveller = time_machine.travel(
            travel_datetime or self.study_open_datetime + timedelta(days=52)
        )
        traveller.start()
        consent_datetime = timezone.now()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=timezone.now() - relativedelta(years=25),
        )
        traveller.stop()
        return consent_datetime

    def create_v3_consent_for_subject(
        self, travel_datetime: datetime | None = None
    ) -> datetime:
        # travel to consent v3 validity period and consent subject
        traveller = time_machine.travel(
            travel_datetime or self.study_open_datetime + timedelta(days=101)
        )
        traveller.start()
        consent_datetime = timezone.now()  # cdef.enf + xx days
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=timezone.now() - relativedelta(years=25),
        )
        traveller.stop()
        return consent_datetime

    def test_is_v2_within_v2_consent_period(self):
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        self.create_v3_consent_for_subject()

        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)

        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=consent1_v3.start - relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "2.0")

    def test_consent_date_is_for_version(self):
        """There should be no-gap! If they haven't signed V3 then
        data entry must stop unless there is overlap. In the case
        of overlap. the higher version consent should be used.
        """
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        v3_consent_datetime = self.create_v3_consent_for_subject(
            travel_datetime=consent1_v3.start + relativedelta(days=10)
        )
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
        consent1_v3_new = consent_factory(
            proxy_model="clinicedc_tests.subjectconsentv3",
            start=self.study_open_datetime + timedelta(days=120),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates=consent1_v2,
        )
        site_consents.registry = {}
        site_consents.register(consent1_v1)
        site_consents.register(consent1_v2, updated_by=consent1_v3_new)
        site_consents.register(consent1_v3_new)

        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()

        # cannot consent, date does not fall within a consent period
        traveller = time_machine.travel(consent1_v3_new.start - relativedelta(days=10))
        traveller.start()
        consent_datetime = timezone.now()
        self.assertRaises(
            ConsentDefinitionDoesNotExist,
            site_consents.get_consent_definition,
            report_datetime=consent_datetime,
        )
        traveller.stop()

        # ok, date does falls within a consent period
        traveller = time_machine.travel(consent1_v3_new.start)
        traveller.start()
        consent_datetime = timezone.now()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        baker.make_recipe(
            cdef.model,
            subject_identifier=self.subject_identifier,
            identity=self.identity,
            confirm_identity=self.identity,
            consent_datetime=consent_datetime,
            dob=timezone.now() - relativedelta(years=25),
        )
        traveller.stop()

    def test_is_v3_on_v3_consent_date(self):
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        v3_consent_datetime = self.create_v3_consent_for_subject()
        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)
        traveller = time_machine.travel(v3_consent_datetime)
        traveller.start()
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=v3_consent_datetime,
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")
        traveller.stop()

    def test_is_v3_on_after_v3_consent_date(self):
        self.create_v1_consent_for_subject()
        self.create_v2_consent_for_subject()
        v3_consent_datetime = self.create_v3_consent_for_subject()

        self.assertEqual(SubjectConsent.objects.filter(identity=self.identity).count(), 3)

        traveller = time_machine.travel(v3_consent_datetime)
        traveller.start()
        consent = site_consents.get_consent_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=v3_consent_datetime + relativedelta(days=5),
            site_id=settings.SITE_ID,
        )
        self.assertEqual(consent.version, "3.0")
        traveller.stop()
