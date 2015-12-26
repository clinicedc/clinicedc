import factory

from faker import Factory as FakerFactory
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

from django.utils import timezone

from edc_constants.constants import YES, NO
from edc_consent.models.consent_type import ConsentType

from .base_test_models import TestConsentModel, TestConsentModelProxy

faker = FakerFactory.create()


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
    app_label = 'edc_consent'
    model_name = 'testconsentmodel'
    start_datetime = timezone.now() - timedelta(days=1)
    end_datetime = timezone.now() + timedelta(days=365)
