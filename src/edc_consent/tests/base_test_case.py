import factory

from faker import Factory as FakerFactory

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from django.test import TestCase
from django.utils import timezone

from edc_consent.forms.base_consent_form import BaseConsentForm
from edc_consent.models import BaseConsent, RequiresConsentMixin, ConsentType
from edc_consent.models.fields import (
    IdentityFieldsMixin, SampleCollectionFieldsMixin, PersonalFieldsMixin,
    VulnerabilityFieldsMixin, SiteFieldsMixin)
from edc_constants.constants import YES, NO
from edc_quota.client.models import QuotaMixin, QuotaManager
from edc_consent.models.base_specimen_consent import BaseSpecimenConsent


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
        fields = '__all__'


class ConsentModelProxyForm(BaseConsentForm):

    class Meta:
        model = TestConsentModelProxy
        fields = '__all__'


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


class TestSpecimenConsent(BaseSpecimenConsent):

    class Meta:
        app_label = 'edc_consent'


class BaseTestCase(TestCase):
    pass
