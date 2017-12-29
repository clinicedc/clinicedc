from faker import Faker

from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_identifier.exceptions import SubjectIdentifierError
from edc_protocol import EnrollmentCapReached

from ..models import IdentifierModel
from ..research_identifier import IdentifierMissingTemplateValue
from ..subject_identifier import SubjectIdentifier
from .models import EnrollmentThree, Enrollment
from django.contrib.sites.models import Site


fake = Faker()


class TestSubjectIdentifier(TestCase):

    def test_create(self):
        """Asserts raises exception if cannot find cap.
        """
        try:
            SubjectIdentifier(
                identifier_type='subject',
                model='edc_identifier.enrollment',
                protocol_number='000',
                device_id='99')
        except EnrollmentCapReached:
            self.fail('EnrollmentCapReached unexpectedly raised')

    def test_raises_on_unknown_cap(self):
        """Asserts raises exception if cannot find cap.
        """
        self.assertRaises(
            SubjectIdentifierError,
            SubjectIdentifier,
            identifier_type='subjectblahblah',
            model='edc_identifier.enrollmentblahblahblah',
            protocol_number='000',
            device_id='99')

    def test_increments(self):
        """Asserts identifier sequence increments correctly.
        """
        opts = dict(identifier_type='subject',
                    model='edc_identifier.enrollment')
        for i in range(1, 10):
            subject_identifier = SubjectIdentifier(**opts)
            self.assertEqual(
                subject_identifier.identifier[8:12], '000' + str(i))

    def test_create_missing_args(self):
        """Asserts raises exception for missing identifier_type.
        """
        self.assertRaises(
            SubjectIdentifierError,
            SubjectIdentifier,
            identifier_type='',
            model='edc_identifier.enrollment')

    def test_create_missing_args2(self):
        """Asserts raises exception for missing model.
        """
        self.assertRaises(
            SubjectIdentifierError,
            SubjectIdentifier,
            identifier_type='subject',
            model='')

    def test_create_missing_args3(self):
        """Asserts raises exception for missing site_code.
        """
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.site_code = None
        app_config.ready()
        identifier = SubjectIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            site=1)  # incorrectly not a model instance
        try:
            identifier.identifier
        except IdentifierMissingTemplateValue:
            pass
        else:
            self.fail('IdentifierMissingTemplateValue unexpectedly not raised.')

    def test_create1(self):
        """Asserts exact first identifier given parameters.
        """
        subject_identifier = SubjectIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99')
        self.assertEqual('000-40990001-6', subject_identifier.identifier)

    def test_create2(self):
        """Asserts exact first identifier required parameters and those fetched from edc-example.AppConfig."""
        subject_identifier = SubjectIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000')
        self.assertEqual('000-40140001-5', subject_identifier.identifier)

    def test_create_hits_cap(self):
        """Asserts raises exception if attempt to exceed cap.
        """
        for _ in range(1, 6):
            identifier = SubjectIdentifier(
                identifier_type='subject',
                model='edc_identifier.enrollmentthree',
                protocol_number='000',
                device_id='99')
            EnrollmentThree.objects.create(
                subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        self.assertEqual(IdentifierModel.objects.all().count(), 5)
        self.assertRaises(
            EnrollmentCapReached,
            SubjectIdentifier,
            identifier_type='subject',
            model='edc_identifier.enrollmentthree',
            protocol_number='000',
            device_id='99')

    def test_create_hits_cap_with_other_models(self):
        """Asserts raises exception if attempt to exceed cap.
        """
        for _ in range(0, 10):
            identifier = SubjectIdentifier(
                identifier_type='subject',
                model='edc_identifier.enrollment',
                protocol_number='000',
                device_id='99')
            Enrollment.objects.create(
                subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        for _ in range(0, 5):
            identifier = SubjectIdentifier(
                identifier_type='subject',
                model='edc_identifier.enrollmentthree',
                protocol_number='000',
                device_id='99')
            EnrollmentThree.objects.create(
                subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        self.assertEqual(IdentifierModel.objects.filter(
            model='edc_identifier.enrollmentthree').count(), 5)
        self.assertRaises(
            EnrollmentCapReached,
            SubjectIdentifier,
            identifier_type='subject',
            model='edc_identifier.enrollmentthree',
            protocol_number='000',
            device_id='99')

    def test_updates_identifier_model(self):
        """Asserts updates Identifier model with all attributes.
        """
        for _ in range(0, 5):
            identifier = SubjectIdentifier(
                identifier_type='subject',
                model='edc_identifier.enrollmentthree',
                protocol_number='000',
                device_id='99')
            EnrollmentThree.objects.create(
                subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        self.assertEqual(IdentifierModel.objects.all().count(), 5)
        self.assertEqual(
            IdentifierModel.objects.filter(
                subject_type='subject',
                model='edc_identifier.enrollmentthree',
                protocol_number='000',
                device_id='99').count(), 5)
