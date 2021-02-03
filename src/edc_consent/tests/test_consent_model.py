from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from edc_protocol import Protocol
from edc_utils import get_utcnow
from model_bakery import baker

from ..field_mixins import IdentityFieldsMixinError
from ..site_consents import site_consents
from .consent_test_utils import consent_factory
from .models import SubjectConsent


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestConsentModel(TestCase):
    def setUp(self):
        self.study_open_datetime = Protocol().study_open_datetime
        self.study_close_datetime = Protocol().study_close_datetime
        site_consents.registry = {}
        consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )
        consent_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates_versions="1.0, 2.0",
        )
        self.dob = self.study_open_datetime - relativedelta(years=25)

    def test_encryption(self):
        subject_consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            first_name="ERIK",
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() + relativedelta(years=25),
        )
        self.assertEqual(subject_consent.first_name, "ERIK")

    def test_gets_subject_identifier(self):
        """Asserts a blank subject identifier is set to the
        subject_identifier_as_pk.
        """
        consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=None,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() + relativedelta(years=25),
            site=Site.objects.get_current(),
        )
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(consent.subject_identifier, consent.subject_identifier_as_pk)
        consent.save()
        self.assertIsNotNone(consent.subject_identifier)
        self.assertNotEqual(consent.subject_identifier, consent.subject_identifier_as_pk)

    def test_subject_has_current_consent(self):
        subject_identifier = "123456789"
        identity = "987654321"
        baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=1),
            dob=get_utcnow() + relativedelta(years=25),
        )
        subject_consent = SubjectConsent.consent.consent_for_period(
            "123456789", self.study_open_datetime + timedelta(days=1)
        )
        self.assertEqual(subject_consent.version, "1.0")
        baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=60),
            dob=get_utcnow() + relativedelta(years=25),
        )
        subject_consent = SubjectConsent.consent.consent_for_period(
            "123456789", self.study_open_datetime + timedelta(days=60)
        )
        self.assertEqual(subject_consent.version, "2.0")

    def test_model_updates(self):
        subject_identifier = "123456789"
        identity = "987654321"
        consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() + relativedelta(years=25),
        )
        self.assertEqual(consent.version, "1.0")
        consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=51),
            dob=get_utcnow() + relativedelta(years=25),
        )
        self.assertEqual(consent.version, "2.0")
        consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=get_utcnow() + relativedelta(years=25),
        )
        self.assertEqual(consent.version, "3.0")

    def test_model_updates2(self):
        subject_identifier = "123456789"
        identity = "987654321"
        consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime,
            dob=get_utcnow() + relativedelta(years=25),
        )
        self.assertEqual(consent.version, "1.0")
        consent = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=self.study_open_datetime + timedelta(days=101),
            dob=get_utcnow() + relativedelta(years=25),
        )
        self.assertEqual(consent.version, "3.0")

    def test_manager(self):
        for i in range(1, 3):
            baker.make_recipe(
                "edc_consent.subjectconsent",
                subject_identifier=str(i),
                consent_datetime=self.study_open_datetime + relativedelta(days=i),
            )

        first = SubjectConsent.objects.get(subject_identifier="1")
        self.assertEqual(first, SubjectConsent.consent.first_consent(subject_identifier="1"))

        SubjectConsent.consent.consent_for_period(
            subject_identifier="1",
            report_datetime=self.study_open_datetime + relativedelta(days=1),
        )
        self.assertEqual(first, SubjectConsent.consent.first_consent(subject_identifier="1"))

        self.assertIsNone(
            SubjectConsent.consent.consent_for_period(
                subject_identifier="A",
                report_datetime=self.study_open_datetime - relativedelta(days=1),
            )
        )

        self.assertIsNone(
            SubjectConsent.consent.consent_for_period(
                subject_identifier="A",
                report_datetime=self.study_open_datetime + relativedelta(days=1),
            )
        )

    def test_model_str_repr_etc(self):
        obj = baker.make_recipe(
            "edc_consent.subjectconsent",
            subject_identifier="12345",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
        )
        self.assertTrue(str(obj))
        self.assertTrue(repr(obj))
        self.assertTrue(obj.age_at_consent)
        self.assertTrue(obj.formatted_age_at_consent)
        self.assertEqual(obj.report_datetime, obj.consent_datetime)

        self.assertRaises(
            IdentityFieldsMixinError,
            baker.make_recipe,
            "edc_consent.subjectconsent",
            subject_identifier="12345",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
            identity="123456789",
            confirm_identity="987654321",
        )
