from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from model_mommy import mommy

from ..consent import Consent
from ..site_consents import site_consents
from .dates_test_mixin import DatesTestMixin
from .models import SubjectConsent


class TestConsentModel(DatesTestMixin, TestCase):

    def setUp(self):
        site_consents.reset_registry()
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='2.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version='3.0',
            updates_versions='1.0, 2.0')
        self.dob = self.study_open_datetime - relativedelta(years=25)

    def consent_factory(self, **kwargs):
        options = dict(
            start=kwargs.get('start'),
            end=kwargs.get('end'),
            gender=kwargs.get('gender', ['M', 'F']),
            updates_versions=kwargs.get('updates_versions', []),
            version=kwargs.get('version', '1'),
            age_min=kwargs.get('age_min', 16),
            age_max=kwargs.get('age_max', 64),
            age_is_adult=kwargs.get('age_is_adult', 18),
        )
        model = kwargs.get('model', 'edc_consent.subjectconsent')
        consent = Consent(model, **options)
        site_consents.register(consent)
        return consent

    def test_encryption(self):
        subject_consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            first_name='ERIK',
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        self.assertEqual(subject_consent.first_name, 'ERIK')

    def test_gets_subject_identifier(self):
        """Asserts a blank subject identifier is set to the
        subject_identifier_as_pk.
        """
        consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=None,
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            study_site='40')
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(
            consent.subject_identifier, consent.subject_identifier_as_pk)
        consent.save()
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(
            consent.subject_identifier, consent.subject_identifier_as_pk)

    def test_subject_has_current_consent(self):
        subject_identifier = '123456789'
        identity = '987654321'
        mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=1),
            dob=self.get_utcnow() + relativedelta(years=25))
        subject_consent = SubjectConsent.consent.consent_for_period(
            '123456789', self.study_open_datetime + timedelta(days=1))
        self.assertEqual(subject_consent.version, '1.0')
        mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=60),
            dob=self.get_utcnow() + relativedelta(years=25))
        subject_consent = SubjectConsent.consent.consent_for_period(
            '123456789', self.study_open_datetime + timedelta(days=60))
        self.assertEqual(subject_consent.version, '2.0')

    def test_model_updates(self):
        subject_identifier = '123456789'
        identity = '987654321'
        consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        self.assertEqual(consent.version, '1.0')
        consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=51),
            dob=self.dob)
        self.assertEqual(consent.version, '2.0')
        consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=self.dob)
        self.assertEqual(consent.version, '3.0')

    def test_model_updates2(self):
        subject_identifier = '123456789'
        identity = '987654321'
        consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        self.assertEqual(consent.version, '1.0')
        consent = mommy.make_recipe(
            'edc_consent.subjectconsent',
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=self.dob)
        self.assertEqual(consent.version, '3.0')
