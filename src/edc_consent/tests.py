import factory
from faker import Factory as FakerFactory

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.six import StringIO
from django.core.management import call_command

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from edc_consent.models.base_consent import BaseConsent
from edc_consent.models import RequiresConsentMixin
from edc_consent.exceptions import NotConsentedError, ConsentTypeError, ConsentVersionError
from django.utils import timezone
from edc_constants.constants import YES, NO
from edc_quota.client.models import QuotaMixin, QuotaManager
from edc_consent.models.consent_type import ConsentType
from edc_consent.models.fields import (
    IdentityFieldsMixin, SampleCollectionFieldsMixin, PersonalFieldsMixin, SiteFieldsMixin)
from edc_consent.models.validators import AgeTodayValidator
from edc_consent.forms.base_consent_form import BaseConsentForm
from django.test.utils import override_settings
from edc_consent.models.fields.vulnerability_fields_mixin import VulnerabilityFieldsMixin


faker = FakerFactory.create()


class ConsentQuotaMixin(QuotaMixin):

    QUOTA_REACHED_MESSAGE = 'Maximum number of subjects has been reached or exceeded for {}. Got {} >= {}.'

    class Meta:
        abstract = True


class TestConsentModel(
        ConsentQuotaMixin, IdentityFieldsMixin, SampleCollectionFieldsMixin,
        SiteFieldsMixin, PersonalFieldsMixin, VulnerabilityFieldsMixin, BaseConsent):

    quota = QuotaManager()

    class Meta:
        unique_together = (
            ('subject_identifier', 'version'),
            ('identity', 'version'),
            ('first_name', 'dob', 'initials', 'version'))
        app_label = 'edc_consent'


class TestConsentModelProxy(TestConsentModel):

    MAX_AGE_OF_CONSENT = 120
    GENDER_OF_CONSENT = ['M']

    class Meta:
        proxy = True
        app_label = 'edc_consent'


class TestModel(RequiresConsentMixin, models.Model):

    CONSENT_MODEL = TestConsentModel

    subject_identifier = models.CharField(max_length=10)

    report_datetime = models.DateTimeField(default=timezone.now)

    field1 = models.CharField(max_length=10)

    class Meta:
        app_label = 'edc_consent'
        verbose_name = 'Test Model'


class Visit(models.Model):

    subject_identifier = models.CharField(max_length=10)

    report_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'edc_consent'
        verbose_name = 'Visit'


class TestScheduledModel(RequiresConsentMixin, models.Model):

    CONSENT_MODEL = TestConsentModel

    visit = models.ForeignKey(Visit)

    report_datetime = models.DateTimeField(default=timezone.now)

    def get_subject_identifier(self):
        return self.visit.subject_identifier

    class Meta:
        app_label = 'edc_consent'


class ConsentForm(BaseConsentForm):

    class Meta:
        model = TestConsentModel


class ConsentModelProxyForm(BaseConsentForm):

    class Meta:
        model = TestConsentModelProxy


class TestConsentModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = TestConsentModel

    subject_identifier = '12345'
    first_name = factory.LazyAttribute(lambda x: 'E{}'.format(faker.first_name().upper()))
    last_name = factory.LazyAttribute(lambda x: 'E{}'.format(faker.last_name().upper()))
    initials = 'EE'
    gender = 'M'
    consent_datetime = timezone.now()
    dob = date.today() - relativedelta(years=25)
    is_dob_estimated = '-'
    identity = '123156789'
    confirm_identity = '123156789'
    identity_type = 'OMANG'
    is_literate = YES
    is_incarcerated = NO
    witness_name = None
    language = 'en'
    subject_type = 'subject'
    site_code = '10'
    consent_datetime = timezone.now()
    may_store_samples = YES


class TestConsentModelProxyFactory(factory.DjangoModelFactory):

    class Meta:
        model = TestConsentModelProxy

    subject_identifier = '12345'
    first_name = 'ERIK'
    last_name = 'ERIKS'
    initials = 'EE'
    gender = 'M'
    consent_datetime = timezone.now()
    dob = date.today() - relativedelta(years=25)
    is_dob_estimated = '-'
    identity = '123156789'
    confirm_identity = '123156789'
    identity_type = 'OMANG'
    is_literate = YES
    is_incarcerated = NO
    language = 'en'
    subject_type = 'subject'
    site_code = '10'
    consent_datetime = timezone.now()
    may_store_samples = YES


class ConsentTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = ConsentType

    version = '1.0'
    updates_version = None
    app_label = TestConsentModel._meta.app_label
    model_name = TestConsentModel._meta.model_name
    start_datetime = timezone.now() - timedelta(days=1)
    end_datetime = timezone.now() + timedelta(days=365)


class TestConsent(TestCase):

    def setUp(self):
        TestConsentModel.quota.set_quota(2, date.today(), date.today())
        TestConsentModelProxy.quota.set_quota(2, date.today(), date.today())

    def test_raises_error_if_no_consent_type(self):
        self.assertRaises(NotConsentedError, TestModel.objects.create, subject_identifier='12345')

    def test_raises_error_if_no_consent(self):
        ConsentTypeFactory()
        self.assertRaises(NotConsentedError, TestModel.objects.create, subject_identifier='12345')

    def test_allows_create_if_consent(self):
        ConsentTypeFactory()
        TestConsentModelFactory(subject_identifier='12345')
        TestModel.objects.create(subject_identifier='12345')
        TestConsentModelFactory(subject_identifier='12344', identity='12319876', confirm_identity='12319876')
        TestModel.objects.create(subject_identifier='12344')

    def test_cannot_create_consent_without_consent_type_by_datetime(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(ConsentTypeError, TestConsentModelFactory)

    def test_consent_gets_version(self):
        ConsentTypeFactory(version='1.0')
        consent = TestConsentModelFactory()
        self.assertEqual(consent.version, '1.0')

    def test_model_gets_version(self):
        ConsentTypeFactory(version='1.0')
        TestConsentModelFactory()
        test_model = TestModel.objects.create(subject_identifier='12345')
        self.assertEqual(test_model.consent_version, '1.0')

    def test_model_consent_version_no_change(self):
        ConsentTypeFactory(version='1.2')
        TestConsentModelFactory()
        test_model = TestModel.objects.create(subject_identifier='12345')
        self.assertEqual(test_model.consent_version, '1.2')
        test_model.save()
        self.assertEqual(test_model.consent_version, '1.2')

    def test_model_consent_version_changes_with_report_datetime(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=100),
            version='1.1')
        TestConsentModelFactory(consent_datetime=timezone.now() - timedelta(days=300))
        test_model = TestModel.objects.create(
            subject_identifier='12345',
            report_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(test_model.consent_version, '1.0')
        TestConsentModelFactory()
        test_model.report_datetime = timezone.now()
        test_model.save()
        self.assertEqual(test_model.consent_version, '1.1')

    def test_consent_type_update_needs_previous_version(self):
        """Asserts that a consent type updates a previous consent."""
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(
            ConsentTypeError, ConsentTypeFactory,
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=100),
            version='1.1',
            updates_version='1.2')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() - timedelta(days=100),
            version='1.1',
            updates_version='1.0')

    def test_consent_needs_previous_version(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.1',
            updates_version='1.0')
        self.assertRaises(ConsentVersionError, TestConsentModelFactory)

    def test_consent_needs_previous_version2(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.version, '1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.1',
            updates_version='1.0')
        consent = TestConsentModelFactory(
            first_name=consent.first_name,
            last_name=consent.last_name,
            initials=consent.initials)
        self.assertEqual(consent.version, '1.1')

    def test_consent_needs_previous_version3(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.version, '1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() - timedelta(days=50),
            version='1.1',
            updates_version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=49),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.2',
            updates_version='1.1')
        self.assertRaises(ConsentVersionError, TestConsentModelFactory)

    def test_consent_periods_cannot_overlap(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(
            ConsentTypeError, ConsentTypeFactory,
            start_datetime=timezone.now() - timedelta(days=201),
            end_datetime=timezone.now(),
            version='1.1',
            updates_version='1.0')

    def test_consent_periods_cannot_overlap2(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        self.assertRaises(
            ConsentTypeError, ConsentTypeFactory,
            start_datetime=timezone.now() - timedelta(days=201),
            end_datetime=timezone.now() + timedelta(days=201),
            version='1.1')

    def test_encryption(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(
            first_name='ERIK',
            consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.first_name, 'ERIK')

    def test_no_subject_identifier(self):
        """Asserts a blank subject identifier is set to the subject_identifier_as_pk."""
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(
            subject_identifier=None, consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.subject_identifier, consent.subject_identifier_as_pk)
        consent.subject_identifier = '12345'
        consent.save()
        self.assertEqual(consent.subject_identifier, '12345')

    def test_consent_age_validator(self):
        validator = AgeTodayValidator(16, 64)
        self.assertIsNone(validator(date.today() - relativedelta(years=25)))
        self.assertRaises(ValidationError, validator, date.today() - relativedelta(years=15))
        self.assertRaises(ValidationError, validator, date.today() - relativedelta(years=65))

    def test_constants(self):
        self.assertEqual(TestConsentModel.MAX_AGE_OF_CONSENT, 64)
        self.assertEqual(TestConsentModelProxy.MAX_AGE_OF_CONSENT, 120)

    def test_subject_has_current_consent(self):
        subject_identifier = '123456789'
        identity = '987654321'
        report_datetime = timezone.now() - timedelta(days=1)
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() + timedelta(days=200),
            version='2.0')
        TestConsentModelFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=timezone.now() - timedelta(days=300))
        self.assertIsNone(TestConsentModel.consent.valid_consent_for_period(
            '123456789', report_datetime))
        TestConsentModelFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=report_datetime)
        self.assertIsNotNone(TestConsentModel.consent.valid_consent_for_period(
            '123456789', report_datetime))

    def test_consent_may_updates_more_than_one_version(self):
        subject_identifier = '123456789'
        identity = '987654321'
        report_datetime = timezone.now() - timedelta(days=1)
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=timezone.now() - timedelta(days=300))
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=199),
            end_datetime=timezone.now() - timedelta(days=50),
            version='2.0',
            updates_version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=49),
            end_datetime=timezone.now() + timedelta(days=200),
            version='3.0',
            updates_version='1.0,2.0')
        TestConsentModelFactory(
            first_name=consent.first_name,
            last_name=consent.last_name,
            initials=consent.initials,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=report_datetime)

    def test_scheduled_model_with_fk(self):
        subject_identifier = '123456789'
        identity = '987654321'
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        TestConsentModelFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity)
        visit = Visit.objects.create(subject_identifier=subject_identifier)
        TestScheduledModel.objects.create(visit=visit)

    def test_base_form_is_valid(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory.build()
        consent_form = ConsentForm(data=consent.__dict__)
        print(consent_form.errors)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_identity_mismatch(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory()
        consent.confirm_identity = '1'
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(u'Identity mismatch', ','.join(consent_form.non_field_errors()))

    def test_base_form_identity_dupl(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=100),
            version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='2.0')
        consent1 = TestConsentModelFactory()
        consent1.save()
        consent2 = TestConsentModelFactory(
            subject_identifier='123455',
            identity='123156788', confirm_identity='123156788')
        consent2.identity = consent1.identity
        consent2.confirm_identity = consent1.confirm_identity
        consent_form = ConsentForm(data=consent2.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn('Identity \'123156789\' is already in use by subject 12345', ','.join(
            consent_form.non_field_errors()))

    def test_base_form_guardian_and_dob1(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory.build()
        consent.guardian_name = None
        consent.dob = timezone.now() - relativedelta(years=TestConsentModel.AGE_IS_ADULT - 1)
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn('Subject is a minor', ','.join(consent_form.non_field_errors()))

    def test_base_form_guardian_and_dob2(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory.build()
        consent.guardian_name = 'SPOCK, YOUCOULDNTPRONOUNCEIT'
        consent.dob = timezone.now() - relativedelta(years=TestConsentModel.AGE_IS_ADULT)
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn('Subject is an adult', ','.join(consent_form.non_field_errors()))

    def test_base_form_guardian_and_dob3(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory.build()
        consent.dob = timezone.now() - relativedelta(years=TestConsentModel.AGE_IS_ADULT)
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_catches_dob_lower(self):
        subject_identifier = '123456789'
        identity = '987654321'
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            dob=date.today())
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Subject\'s age is 0d. Subject is not eligible for consent.',
            ','.join(consent_form.non_field_errors()))

    def test_base_form_catches_dob_upper(self):
        subject_identifier = '123456789'
        identity = '987654321'
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            dob=date.today() - relativedelta(years=100))
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Subject\'s age is 100y. Subject is not eligible for consent.',
            ','.join(consent_form.non_field_errors()))

    def test_base_form_catches_gender_of_consent(self):
        ConsentTypeFactory(
            app_label=TestConsentModelProxy._meta.app_label,
            model_name=TestConsentModelProxy._meta.model_name,
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelProxyFactory.build(gender='F')
        consent_form = ConsentModelProxyForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Gender of consent can only be \'M\'. Got \'F\'.',
            ','.join(consent_form.errors.get('gender')))
        consent = TestConsentModelProxyFactory.build(gender='M')
        consent_form = ConsentModelProxyForm(data=consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_catches_is_literate_and_witness(self):
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory(is_literate=NO)
        consent_form = ConsentModelProxyForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'subject is illiterate',
            ','.join(consent_form.non_field_errors()))
        consent.witness_name = 'X'
        consent_form = ConsentModelProxyForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Format is \'LASTNAME, FIRSTNAME\'',
            ','.join(consent_form.errors.get('witness_name')))
        consent.witness_name = 'SPOCK, YOUCOULDNTPRONOUNCEIT'
        consent_form = ConsentModelProxyForm(data=consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    @override_settings(STUDY_OPEN_DATETIME=timezone.datetime.today() - relativedelta(years=3))
    def test_base_form_catches_consent_datetime_before_study_open(self):
        study_open_date = (timezone.datetime.today() - relativedelta(years=3)).date().isoformat()
        subject_identifier = '123456789'
        identity = '987654321'
        ConsentTypeFactory(
            start_datetime=timezone.now() - relativedelta(years=5),
            end_datetime=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = TestConsentModelFactory.build(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=timezone.now() - relativedelta(years=4),
            dob=date.today() - relativedelta(years=25))
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        validation_message = ','.join(consent_form.errors.get('consent_datetime'))
        self.assertIn('Invalid date. Study opened on {}'.format(study_open_date),
                      validation_message)
        consent = TestConsentModelFactory.build(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=timezone.now() - relativedelta(years=2),
            dob=date.today() - relativedelta(years=25))
        consent_form = ConsentForm(data=consent.__dict__)
        self.assertIsNone(consent_form.errors.get('consent_datetime'))

    def test_updateconsentversion_management(self):
        out = StringIO()
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=365),
            end_datetime=timezone.now() - timedelta(days=100),
            version='1.0')
        ConsentTypeFactory(
            start_datetime=timezone.now() - timedelta(days=99),
            end_datetime=timezone.now() + timedelta(days=200),
            version='2.0')
        consent2 = TestConsentModelFactory()
        consent1 = TestConsentModelFactory(
            subject_identifier='987654321',
            identity='123112345', confirm_identity='123112345',
            consent_datetime=timezone.now() - timedelta(days=150))
        consent1.version = '?'
        consent2.version = '?'
        consent1.save_base(update_fields=['version'])
        consent2.save_base(update_fields=['version'])
        consent1 = TestConsentModel.objects.get(pk=consent1.pk)
        consent2 = TestConsentModel.objects.get(pk=consent2.pk)
        self.assertEqual(consent1.version, '?')
        self.assertEqual(consent2.version, '?')
        call_command('updateconsentversion', stdout=out)
        self.assertIn('Found consents: {}'.format(TestConsentModel._meta.verbose_name), out.getvalue())
        self.assertIn("Updating {} \'{}\' where version == \'?\' ... ".format(
            2, TestConsentModel._meta.verbose_name), out.getvalue())
        consent1 = TestConsentModel.objects.get(pk=consent1.pk)
        consent2 = TestConsentModel.objects.get(pk=consent2.pk)
        self.assertEqual(consent1.version, '1.0')
        self.assertEqual(consent2.version, '2.0')
