from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from edc_consent.models.base_consent import BaseConsent
from edc_consent.models import RequiresConsentMixin
from edc_consent.exceptions import NotConsentedError, ConsentTypeError, ConsentVersionError
from django.utils import timezone
from edc_constants.constants import YES
from edc_quota.client.models import QuotaMixin, QuotaManager
from edc_consent.models.consent_type import ConsentType
from edc_consent.models.fields import (
    IdentityFieldsMixin, SampleCollectionFieldsMixin, PersonalFieldsMixin, SiteFieldsMixin)
from edc_consent.validators import ConsentAgeValidator


class ConsentQuotaMixin(QuotaMixin):

    QUOTA_REACHED_MESSAGE = 'Maximum number of subjects has been reached or exceeded for {}. Got {} >= {}.'

    class Meta:
            abstract = True


class TestConsentModel(
        ConsentQuotaMixin, IdentityFieldsMixin, SampleCollectionFieldsMixin,
        SiteFieldsMixin, PersonalFieldsMixin, BaseConsent):

    quota = QuotaManager()

    objects = models.Manager()

    class Meta:
        app_label = 'edc_consent'


class TestConsentModel2(TestConsentModel):

    class Constants(PersonalFieldsMixin.Constants):
        MAX_AGE_OF_CONSENT = 120

    class Meta:
        proxy = True


class TestModel(RequiresConsentMixin, models.Model):

    CONSENT_MODEL = TestConsentModel

    subject_identifier = models.CharField(max_length=10)

    report_datetime = models.DateTimeField(default=timezone.now)

    field1 = models.CharField(max_length=10)

    class Meta:
        app_label = 'edc_consent'
        verbose_name = 'Test Model'


class TestConsent(TestCase):

    def setUp(self):
        TestConsentModel.quota.set_quota(2, date.today(), date.today())

    def create_consent_type(self, start_datetime=None, end_datetime=None, version=None, updates_version=None):
        return ConsentType.objects.create(
            version=version or '1.0',
            updates_version=updates_version,
            app_label=TestConsentModel._meta.app_label,
            model_name=TestConsentModel._meta.model_name,
            start_datetime=start_datetime or timezone.now() - timedelta(days=1),
            end_datetime=end_datetime or timezone.now() + timedelta(days=365)
        )

    def create_consent(self, subject_identifier, identity, consent_datetime=None, dob=None):
        consent_datetime = consent_datetime or timezone.now()
        return TestConsentModel.objects.create(
            subject_identifier=subject_identifier,
            first_name='ERIK',
            last_name='ERIKS',
            dob=dob or (date.today() - relativedelta(years=25)),
            identity=identity,
            confirm_identity=identity,
            subject_type='study',
            site_code='10',
            consent_datetime=consent_datetime,
            may_store_samples=YES,
        )

    def test_raises_error_if_no_consent_type(self):
        self.assertRaises(ConsentTypeError, TestModel.objects.create, subject_identifier='12345')

    def test_raises_error_if_no_consent(self):
        self.create_consent_type()
        self.assertRaises(NotConsentedError, TestModel.objects.create, subject_identifier='12345')

    def test_allows_create_if_consent(self):
        self.create_consent_type()
        self.create_consent('12345', '123456789')
        TestModel.objects.create(subject_identifier='12345')
        self.create_consent('12344', '123456788')
        TestModel.objects.create(subject_identifier='12344')

    def test_cannot_create_consent_without_type_by_datetime(self):
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(ConsentTypeError, self.create_consent, '12345', '123456789', timezone.now())

    def test_consent_gets_version(self):
        self.create_consent_type(version='1.0')
        consent = self.create_consent('12345', '123456789', timezone.now())
        self.assertEqual(consent.version, '1.0')

    def test_model_gets_version(self):
        self.create_consent_type(version='1.0')
        self.create_consent('12345', '123456789', timezone.now())
        test_model = TestModel.objects.create(subject_identifier='12345')
        self.assertEqual(test_model.consent_version, '1.0')

    def test_model_consent_version_no_change(self):
        self.create_consent_type(version='1.2')
        self.create_consent('12345', '123456789', timezone.now())
        test_model = TestModel.objects.create(subject_identifier='12345')
        self.assertEqual(test_model.consent_version, '1.2')
        test_model.save()
        self.assertEqual(test_model.consent_version, '1.2')

    def test_model_consent_version_changes(self):
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=100),
            version='1.1')
        self.create_consent('12345', '123456789', timezone.now() - timedelta(days=300))
        test_model = TestModel.objects.create(subject_identifier='12345',
                                              report_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(test_model.consent_version, '1.0')
        self.create_consent('12345', '123456789', timezone.now())
        test_model.report_datetime = timezone.now()
        test_model.save()
        self.assertEqual(test_model.consent_version, '1.1')

    def test_consent_type_update_needs_previous_version(self):
        """Asserts that a consent type updates a previous consent."""
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(
            ConsentTypeError, self.create_consent_type,
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=100),
            version='1.1',
            updates_version='1.2')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() - timedelta(days=100),
            version='1.1',
            updates_version='1.0')

    def test_consent_needs_previous_version(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.1',
            updates_version='1.0')
        self.assertRaises(ConsentVersionError, self.create_consent, '12345', '123456789', timezone.now())

    def test_consent_needs_previous_version2(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = self.create_consent('12345', '123456789', timezone.now() - timedelta(days=300))
        self.assertEqual(consent.version, '1.0')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.1',
            updates_version='1.0')
        consent = self.create_consent('12345', '123456789', timezone.now())
        self.assertEqual(consent.version, '1.1')

    def test_consent_needs_previous_version3(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = self.create_consent('12345', '123456789', timezone.now() - timedelta(days=300))
        self.assertEqual(consent.version, '1.0')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() - timedelta(days=50),
            version='1.1',
            updates_version='1.0')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=49),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.2',
            updates_version='1.1')
        self.assertRaises(ConsentVersionError, self.create_consent, '12345', '123456789', timezone.now())

    def test_consent_periods_cannot_overlap(self):
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(
            ConsentTypeError, self.create_consent_type,
            start_datetime=timezone.now() - timedelta(days=201),
            end_datetime=timezone.now(),
            version='1.1',
            updates_version='1.0')

    def test_consent_periods_cannot_overlap2(self):
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        self.assertRaises(
            ConsentTypeError, self.create_consent_type,
            start_datetime=timezone.now() - timedelta(days=201),
            end_datetime=timezone.now() + timedelta(days=201),
            version='1.1')

    def test_encryption(self):
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = self.create_consent('12345', '123456789', timezone.now() - timedelta(days=300))
        self.assertEqual(consent.first_name, 'ERIK')

    def test_no_subject_identifier(self):
        """Asserts a blank subject identifier is set to the subject_identifier_as_pk."""
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = self.create_consent(None, '123456789', timezone.now() - timedelta(days=300))
        self.assertEqual(consent.subject_identifier, consent.subject_identifier_as_pk)
        consent.subject_identifier = '123456789'
        consent.save()
        self.assertEqual(consent.subject_identifier, '123456789')

    def test_consent_age_validator(self):
        validator = ConsentAgeValidator(16, 64)
        self.assertIsNone(validator(date.today() - relativedelta(years=25)))
        self.assertRaises(ValidationError, validator, date.today() - relativedelta(years=15))
        self.assertRaises(ValidationError, validator, date.today() - relativedelta(years=65))

    def test_constants(self):
        self.assertEqual(TestConsentModel.Constants.MAX_AGE_OF_CONSENT, 64)
        self.assertEqual(TestConsentModel2.Constants.MAX_AGE_OF_CONSENT, 120)

    def test_subject_has_current_consent(self):
        subject_identifier = '123456789'
        identity = '987654321'
        report_datetime = timezone.now() - timedelta(days=1)
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.create_consent_type(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=200),
            version='2.0')
        self.create_consent(subject_identifier, identity, timezone.now() - timedelta(days=300))
        self.assertIsNone(TestConsentModel.consent.valid_consent_for_period(
            '123456789', report_datetime))
        self.create_consent(subject_identifier, identity, report_datetime)
        self.assertIsNotNone(TestConsentModel.consent.valid_consent_for_period(
            '123456789', report_datetime))
