from datetime import timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker
from model_mommy import mommy

from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_appointment.models import Appointment
from edc_base_test.mixins import DatesTestMixin

from ..consent import Consent
from ..exceptions import (
    NotConsentedError, ConsentPeriodError,
    ConsentVersionSequenceError, ConsentPeriodOverlapError)
from ..site_consents import site_consents
from edc_consent.exceptions import ConsentDoesNotExist

fake = Faker()


class TestConsent(DatesTestMixin, TestCase):

    def setUp(self):
        site_consents.reset_registry()
        self.dob = self.study_open_datetime - relativedelta(years=25)

    def consent_factory(self, **kwargs):
        options = dict(
            start=kwargs.get('start', self.study_open_datetime),
            end=kwargs.get('end', self.study_close_datetime),
            gender=kwargs.get('gender', ['M', 'F']),
            updates_versions=kwargs.get('updates_versions', []),
            version=kwargs.get('version', '1'),
            age_min=kwargs.get('age_min', 16),
            age_max=kwargs.get('age_max', 64),
            age_is_adult=kwargs.get('age_is_adult', 18),
        )
        model = kwargs.get('model', 'edc_example.subjectconsent')
        consent = Consent(model, **options)
        site_consents.register(consent)
        return consent

    def test_raises_error_if_no_consent(self):
        """Asserts SubjectConsent cannot create a new instance if
        no consents are defined.

        Note: site_consents.reset_registry called in setUp.
        """
        subject_identifier = '12345'
        self.assertRaises(
            ConsentDoesNotExist,
            mommy.make_recipe,
            'edc_example.subjectconsent',
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime)

    def test_raises_error_if_no_consent2(self):
        """Asserts a model using the RequiresConsentMixin cannot create
        a new instance if subject not consented.
        """
        self.consent_factory()
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        RegisteredSubject.objects.create(subject_identifier='12345')
        self.assertRaises(
            NotConsentedError,
            mommy.make_recipe,
            'edc_example.enrollment',
            subject_identifier='12345',
            report_datetime=self.study_open_datetime)

    def test_allows_create_if_consent(self):
        """Asserts can create a consent model instance if a valid
        consent.
        """
        self.consent_factory()
        subject_identifier = '12345'
        mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_identifier,
            report_datetime=self.study_open_datetime,
            schedule_name='schedule1')
        self.assertEqual(Appointment.objects.all().count(), 4)

    def test_cannot_create_consent_without_consent_by_datetime(self):
        """Asserts can create a consent model instance if a matching
        consent in site_consents.
        """
        self.consent_factory(
            start=self.study_open_datetime + relativedelta(days=5),
            end=self.study_close_datetime,
            version='1.0')
        self.assertRaises(
            ConsentDoesNotExist,
            mommy.make_recipe,
            'edc_example.subjectconsent',
            dob=self.dob,
            consent_datetime=self.study_open_datetime)

    def test_consent_gets_version(self):
        self.consent_factory(version='1.0')
        consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        self.assertEqual(consent.version, '1.0')

    def test_model_gets_version(self):
        self.consent_factory(version='1.0')
        subject_identifier = '12345'
        mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_identifier,
            report_datetime=self.study_open_datetime,
            schedule_name='schedule1')
        self.assertEqual(enrollment.consent_version, '1.0')

    def test_model_consent_version_no_change(self):
        self.consent_factory(version='1.2')
        subject_identifier = '12345'
        mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier=subject_identifier,
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_identifier,
            report_datetime=self.study_open_datetime,
            schedule_name='schedule1')
        self.assertEqual(enrollment.consent_version, '1.2')
        enrollment.save()
        self.assertEqual(enrollment.consent_version, '1.2')

    def test_model_consent_version_changes_with_report_datetime(self):
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1')
        subject_identifier = '12345'
        consent_datetime = self.study_open_datetime + timedelta(days=10)
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            dob=self.dob)
        self.assertEqual(subject_consent.version, '1.0')
        self.assertEqual(
            subject_consent.subject_identifier, subject_identifier)
        self.assertEqual(subject_consent.consent_datetime, consent_datetime)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_identifier,
            schedule_name='schedule1',
            report_datetime=consent_datetime)
        self.assertEqual(enrollment.consent_version, '1.0')
        consent_datetime = self.study_open_datetime + timedelta(days=60)
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier=subject_identifier,
            consent_datetime=consent_datetime,
            dob=self.dob)
        enrollment.report_datetime = consent_datetime
        enrollment.save()
        self.assertEqual(enrollment.consent_version, '1.1')

    def test_consent_update_needs_previous_version(self):
        """Asserts that a consent type updates a previous consent."""
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        # specify updates version that does not exist, raises
        self.assertRaises(
            ConsentVersionSequenceError, self.consent_factory,
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1',
            updates_versions='1.2')
        # specify updates version that exists, ok
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1',
            updates_versions='1.0')

    def test_consent_model_needs_previous_version(self):
        """Asserts that a consent updates a previous consent but cannot
        be entered without an existing instance for the previous
        version."""
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1',
            updates_versions='1.0')
        self.assertRaises(
            ConsentVersionSequenceError,
            mommy.make_recipe,
            'edc_example.subjectconsent',
            dob=self.dob,
            consent_datetime=self.study_open_datetime + timedelta(days=60))

    def test_consent_needs_previous_version2(self):
        """Asserts that a consent model updates its previous consent.
        """
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1',
            updates_versions='1.0')
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=self.study_open_datetime + timedelta(days=5),
            dob=self.dob)
        self.assertEqual(subject_consent.version, '1.0')
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier=subject_consent.subject_identifier,
            consent_datetime=self.study_open_datetime + timedelta(days=60),
            first_name=subject_consent.first_name,
            last_name=subject_consent.last_name,
            initials=subject_consent.initials,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            dob=subject_consent.dob)
        self.assertEqual(subject_consent.version, '1.1')

    def test_consent_needs_previous_version3(self):
        """Asserts that a consent updates a previous consent raises
        if a version is skipped.
        """
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1',
            updates_versions='1.0')
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version='1.2',
            updates_versions='1.1')
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=self.study_open_datetime,
            dob=self.dob)
        self.assertEqual(subject_consent.version, '1.0')
        # use a consent datetime within verion 1.2, skipping 1.1, raises
        self.assertRaises(
            ConsentVersionSequenceError,
            mommy.make_recipe,
            'edc_example.subjectconsent',
            consent_datetime=self.study_open_datetime + timedelta(days=125),
            subject_identifier=subject_consent.subject_identifier,
            first_name=subject_consent.first_name,
            last_name=subject_consent.last_name,
            initials=subject_consent.initials,
            identity=subject_consent.identity,
            confirm_identity=subject_consent.identity,
            dob=subject_consent.dob)

    def test_consent_periods_cannot_overlap(self):
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.assertRaises(
            ConsentPeriodOverlapError, self.consent_factory,
            start=self.study_open_datetime + timedelta(days=25),
            end=self.study_open_datetime + timedelta(days=100),
            version='1.1',
            updates_versions='1.0')

    def test_consent_periods_cannot_overlap2(self):
        self.consent_factory(
            app_label='example',
            model_name='testconsentmodel',
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.assertRaises(
            ConsentPeriodOverlapError, self.consent_factory,
            app_label='example',
            model_name='testconsentmodel',
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.1')

    def test_consent_periods_can_overlap_if_different_model(self):
        self.consent_factory(
            model='example.testconsentmodel1',
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        try:
            self.consent_factory(
                model='example.testconsentmodel2',
                start=self.study_open_datetime,
                end=self.study_open_datetime + timedelta(days=50),
                version='1.0')
        except ConsentPeriodOverlapError:
            self.fail('ConsentPeriodOverlapError unexpectedly raised')

    def test_consent_before_open(self):
        """Asserts cannot register a consent with a start date
        before the study open date.
        """
        study_open_datetime = django_apps.get_app_config(
            'edc_protocol').study_open_datetime
        study_close_datetime = django_apps.get_app_config(
            'edc_protocol').study_close_datetime
        self.assertRaises(
            ConsentPeriodError,
            self.consent_factory,
            start=study_open_datetime - relativedelta(days=1),
            end=study_close_datetime + relativedelta(days=1),
            version='1.0')

    def test_consent_may_update_more_than_one_version(self):
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
