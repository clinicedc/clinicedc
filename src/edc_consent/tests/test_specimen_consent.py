from datetime import timedelta, date

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from .base_test_case import (
    BaseTestCase, TestConsentModel, TestConsentModelFactory, TestConsentModelProxy, ConsentTypeFactory)


class TestSpecimenConsent(BaseTestCase):

    def setUp(self):
        TestConsentModel.quota.set_quota(2, date.today(), date.today())
        TestConsentModelProxy.quota.set_quota(2, date.today(), date.today())
        self.subject_identifier = '123456789'
        self.identity = '987654321'
        ConsentTypeFactory(
            start_datetime=timezone.now() - relativedelta(years=5),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        self.study_consent = TestConsentModelFactory(
            subject_identifier=self.subject_identifier, identity=self.identity, confirm_identity=self.identity,
            consent_datetime=timezone.now(),
            dob=date.today() - relativedelta(years=25))
