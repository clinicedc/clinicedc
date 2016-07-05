from datetime import timedelta, date

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from .factories import TestConsentModelFactory
from django.test.testcases import TestCase
from edc_consent.consent_type import site_consent_types
from edc_consent.tests.factories import consent_type_factory


class TestSpecimenConsent(TestCase):

    def setUp(self):
        # TestConsentModel.quota.set_quota(2, date.today(), date.today())
        # TestConsentModelProxy.quota.set_quota(2, date.today(), date.today())
        site_consent_types.reset_registry()
        self.subject_identifier = '123456789'
        self.identity = '987654321'
        consent_type_factory(
            start_datetime=timezone.now() - relativedelta(years=5),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        self.study_consent = TestConsentModelFactory(
            subject_identifier=self.subject_identifier, identity=self.identity, confirm_identity=self.identity,
            consent_datetime=timezone.now(),
            dob=date.today() - relativedelta(years=25))
