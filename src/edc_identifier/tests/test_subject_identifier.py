from django.apps import apps as django_apps
from django.test import override_settings, TestCase, tag
from edc_identifier.exceptions import SubjectIdentifierError, IdentifierError
from faker import Faker
from unittest.case import skip

from multisite import SiteID

from ..models import IdentifierModel
from ..research_identifier import IdentifierMissingTemplateValue
from ..subject_identifier import SubjectIdentifier
from .models import EnrollmentThree, Enrollment

fake = Faker()


class TestSubjectIdentifier(TestCase):
    def test_create(self):
        """Asserts raises exception if cannot find cap.
        """
        subject_identifier = SubjectIdentifier(
            identifier_type="subject",
            requesting_model="edc_identifier.enrollment",
            protocol_number="000",
            device_id="99",
        )
        self.assertTrue(subject_identifier.identifier)

    @skip("enrollment cap not implemented")
    def test_raises_on_unknown_cap(self):
        """Asserts raises exception if cannot find cap.
        """
        self.assertRaises(
            SubjectIdentifierError,
            SubjectIdentifier,
            identifier_type="subjectblahblah",
            requesting_model="edc_identifier.enrollmentblahblahblah",
            protocol_number="000",
            device_id="99",
        )

    def test_increments(self):
        """Asserts identifier sequence increments correctly.
        """
        opts = dict(
            identifier_type="subject", requesting_model="edc_identifier.enrollment"
        )
        for i in range(1, 10):
            subject_identifier = SubjectIdentifier(**opts)
            self.assertEqual(subject_identifier.identifier[7:11], "000" + str(i))

    def test_create_missing_args(self):
        """Asserts raises exception for missing identifier_type.
        """
        self.assertRaises(
            IdentifierError,
            SubjectIdentifier,
            identifier_type="",
            requesting_model="edc_identifier.enrollment",
        )

    def test_create_missing_args2(self):
        """Asserts raises exception for missing model.
        """
        self.assertRaises(
            IdentifierError,
            SubjectIdentifier,
            identifier_type="subject",
            requesting_model="",
        )

    def test_create1(self):
        """Asserts exact first identifier given parameters.
        """
        subject_identifier = SubjectIdentifier(
            identifier_type="subject",
            requesting_model="edc_identifier.enrollment",
            protocol_number="000",
            device_id="99",
        )
        self.assertEqual("000-1990001-8", subject_identifier.identifier)

    def test_create2(self):
        """Asserts exact first identifier required parameters
        and those fetched from edc-example.AppConfig.
        """
        subject_identifier = SubjectIdentifier(
            identifier_type="subject",
            requesting_model="edc_identifier.enrollment",
            protocol_number="000",
        )
        self.assertEqual("000-1140001-7", subject_identifier.identifier)

    @skip("enrollment cap not implemented")
    def test_create_hits_cap(self):
        """Asserts raises exception if attempt to exceed cap.
        """
        for _ in range(1, 6):
            identifier = SubjectIdentifier(
                identifier_type="subject",
                requesting_model="edc_identifier.enrollmentthree",
                protocol_number="000",
                device_id="99",
            )
            EnrollmentThree.objects.create(subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        self.assertEqual(IdentifierModel.objects.all().count(), 5)
        self.assertRaises(
            Exception,
            SubjectIdentifier,
            identifier_type="subject",
            requesting_model="edc_identifier.enrollmentthree",
            protocol_number="000",
            device_id="99",
        )

    @skip("enrollment cap not implemented")
    def test_create_hits_cap_with_other_models(self):
        """Asserts raises exception if attempt to exceed cap.
        """
        for _ in range(0, 10):
            identifier = SubjectIdentifier(
                identifier_type="subject",
                requesting_model="edc_identifier.enrollment",
                protocol_number="000",
                device_id="99",
            )
            Enrollment.objects.create(subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        for _ in range(0, 5):
            identifier = SubjectIdentifier(
                identifier_type="subject",
                requesting_model="edc_identifier.enrollmentthree",
                protocol_number="000",
                device_id="99",
            )
            EnrollmentThree.objects.create(subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        self.assertEqual(
            IdentifierModel.objects.filter(
                model="edc_identifier.enrollmentthree"
            ).count(),
            5,
        )
        self.assertRaises(
            Exception,
            SubjectIdentifier,
            identifier_type="subject",
            requesting_model="edc_identifier.enrollmentthree",
            protocol_number="000",
            device_id="99",
        )

    def test_updates_identifier_model(self):
        """Asserts updates Identifier model with all attributes.
        """
        for _ in range(0, 5):
            identifier = SubjectIdentifier(
                identifier_type="subject",
                requesting_model="edc_identifier.enrollmentthree",
                protocol_number="000",
                device_id="99",
            )
            EnrollmentThree.objects.create(subject_identifier=identifier.identifier)
            self.assertIsNotNone(identifier.identifier)
        self.assertEqual(IdentifierModel.objects.all().count(), 5)
        self.assertEqual(
            IdentifierModel.objects.filter(
                identifier_type="subject",
                model="edc_identifier.enrollmentthree",
                protocol_number="000",
                device_id="99",
            ).count(),
            5,
        )
