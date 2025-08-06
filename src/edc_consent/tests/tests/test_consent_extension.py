from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase, override_settings
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from model_bakery import baker

from edc_consent import site_consents
from edc_consent.consent_definition_extension import ConsentDefinitionExtension
from edc_consent.tests.consent_test_utils import consent_factory


class TestConsentExtension(TestCase):
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
            self.consent_v1_ext = ConsentDefinitionExtension(
                "consent_app.subjectconsentv11",
                version="1.1",
                start=datetime(2024, 12, 16, tzinfo=ZoneInfo("UTC")),
                extends=self.consent_v1,
                timepoints=list(range(15, 18 + 1)),
            )
            site_consents.register(self.consent_v1, extended_by=self.consent_v1_ext)
            self.dob = self.study_open_datetime - relativedelta(years=25)

        def test_consent_version_extension(self):
            subject_identifier = "123456789"
            identity = "987654321"
            baker.make_recipe(
                "consent_app.subjectconsentv1",
                subject_identifier=subject_identifier,
                identity=identity,
                confirm_identity=identity,
                consent_datetime=self.study_open_datetime + timedelta(days=1),
                dob=get_utcnow() - relativedelta(years=25),
            )
            subject_consent = site_consents.get_consent_or_raise(
                subject_identifier="123456789",
                report_datetime=self.study_open_datetime + timedelta(days=1),
                site_id=settings.SITE_ID,
            )
            self.assertEqual(subject_consent.version, "1.0")
            baker.make_recipe(
                "consent_app.subjectconsentv1ext",
                subject_identifier=subject_identifier,
                identity=identity,
                confirm_identity=identity,
                consent_datetime=self.study_open_datetime + timedelta(days=1),
                dob=get_utcnow() - relativedelta(years=25),
            )
