from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings, tag
from edc_constants.constants import FEMALE, MALE, NO, NOT_APPLICABLE, YES
from edc_protocol import Protocol
from edc_utils import get_utcnow
from faker import Faker
from model_bakery import baker

from edc_consent.consent import Consent
from edc_consent.modelform_mixins import ConsentModelFormMixin
from edc_consent.site_consents import site_consents

from ..models import SubjectConsent

fake = Faker()


class SubjectConsentForm(ConsentModelFormMixin, forms.ModelForm):
    class Meta:
        model = SubjectConsent
        fields = "__all__"


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestConsentForm(TestCase):
    def setUp(self):
        site_consents.registry = {}
        self.study_open_datetime = Protocol().study_open_datetime
        self.study_close_datetime = Protocol().study_close_datetime
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
        )
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=51),
            end=self.study_open_datetime + timedelta(days=100),
            version="2.0",
        )
        self.consent_factory(
            start=self.study_open_datetime + timedelta(days=101),
            end=self.study_open_datetime + timedelta(days=150),
            version="3.0",
            updates_versions="1.0, 2.0",
        )
        self.dob = self.study_open_datetime - relativedelta(years=25)

    @staticmethod
    def consent_factory(**kwargs):
        options = dict(
            start=kwargs.get("start"),
            end=kwargs.get("end"),
            gender=kwargs.get("gender", ["M", "F"]),
            updates_versions=kwargs.get("updates_versions", []),
            version=kwargs.get("version", "1"),
            age_min=kwargs.get("age_min", 16),
            age_max=kwargs.get("age_max", 64),
            age_is_adult=kwargs.get("age_is_adult", 18),
        )
        model = kwargs.get("model", "edc_consent.subjectconsent")
        consent = Consent(model, **options)
        site_consents.register(consent)
        return consent

    def cleaned_data(self, **kwargs):
        cleaned_data = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=25),
            first_name="THING",
            last_name="ONE",
            initials="TO",
            gender=MALE,
            identity="12315678",
            confirm_identity="12315678",
            identity_type="passport",
            is_dob_estimated="-",
            language="en",
            is_literate=YES,
            is_incarcerated=NO,
            study_questions=YES,
            consent_reviewed=YES,
            consent_copy=YES,
            assessment_score=YES,
            consent_signature=YES,
            site=Site.objects.get_current(),
            legal_marriage=NO,
            marriage_certificate=NOT_APPLICABLE,
            subject_type="subject",
            citizen=YES,
            subject_identifier=uuid4().hex,
        )
        cleaned_data.update(**kwargs)
        return cleaned_data

    def test_base_form_is_valid(self):
        """Asserts baker defaults validate."""
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            dob=self.dob,
            consent_datetime=self.study_open_datetime,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent_form = SubjectConsentForm(data=subject_consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_catches_consent_datetime_before_study_open(self):
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent_form = SubjectConsentForm(data=subject_consent.__dict__)
        self.assertTrue(consent_form.is_valid())
        self.assertIsNone(consent_form.errors.get("consent_datetime"))
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime - relativedelta(days=1),
            dob=self.dob,
        )
        data = subject_consent.__dict__
        data["initials"] = data["first_name"][0] + data["last_name"][0]
        consent_form = SubjectConsentForm(data=data)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_identity_mismatch(self):
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.confirm_identity = "1"
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent_form = SubjectConsentForm(data=subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_identity_dupl(self):
        baker.make_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        consent2 = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            identity="123156788",
            confirm_identity="123156788",
        )
        consent_form = SubjectConsentForm(consent2.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_guardian_and_dob1(self):
        """Asserts form for minor is not valid without guardian name."""
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.guardian_name = None
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent = site_consents.get_consent_for_period(
            report_datetime=subject_consent.consent_datetime,
            model=subject_consent._meta.label_lower,
        )
        subject_consent.dob = self.study_open_datetime - relativedelta(
            years=consent.age_is_adult - 1
        )
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_guardian_and_dob2(self):
        """Asserts form for minor is valid with guardian name."""
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        subject_consent.guardian_name = "SPOCK, YOUCOULDNTPRONOUNCEIT"
        consent = site_consents.get_consent_for_period(
            report_datetime=subject_consent.consent_datetime,
            model=subject_consent._meta.label_lower,
        )
        subject_consent.dob = self.study_open_datetime - relativedelta(
            years=consent.age_is_adult - 1
        )
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_guardian_and_dob3(self):
        """Asserts form for adult is valid."""
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent = site_consents.get_consent_for_period(
            report_datetime=subject_consent.consent_datetime,
            model=subject_consent._meta.label_lower,
        )
        subject_consent.dob = self.study_open_datetime - relativedelta(
            years=consent.age_is_adult
        )
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_guardian_and_dob4(self):
        """Asserts form for adult is not valid if guardian name
        specified.
        """
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        subject_consent.guardian_name = "SPOCK, YOUCOULDNTPRONOUNCEIT"
        consent = site_consents.get_consent_for_period(
            report_datetime=subject_consent.consent_datetime,
            model=subject_consent._meta.label_lower,
        )
        subject_consent.dob = self.study_open_datetime - relativedelta(
            years=consent.age_is_adult
        )
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_catches_dob_lower(self):
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob + relativedelta(years=25),
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_catches_dob_upper(self):
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob - relativedelta(years=100),
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_catches_gender_of_consent(self):
        site_consents.registry = {}
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
            gender=[MALE],
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            gender=MALE,
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        form = SubjectConsentForm(subject_consent.__dict__)
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        self.assertTrue(form.is_valid())
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            gender=FEMALE,
        )
        form = SubjectConsentForm(subject_consent.__dict__)
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        self.assertFalse(form.is_valid())

    def test_base_form_catches_is_literate_and_witness(self):
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            is_literate=NO,
            witness_name="",
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(form.is_valid())
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            is_literate=NO,
            witness_name="BOND, JAMES",
            first_name="ERIK",
            last_name="THEPLEEB",
        )
        subject_consent.initials = subject_consent.first_name[0] + subject_consent.last_name[0]
        form = SubjectConsentForm(subject_consent.__dict__)
        self.assertTrue(form.is_valid())

    def test_ok(self):
        form = SubjectConsentForm(data=self.cleaned_data())
        self.assertTrue(form.is_valid())

    @tag("1")
    def test_raises_on_duplicate_identity1(self):
        form = SubjectConsentForm(data=self.cleaned_data(), instance=SubjectConsent())
        self.assertTrue(form.is_valid())
        subject_consent = form.save(commit=True)

        subject_consent.refresh_from_db()
        form = SubjectConsentForm(data=subject_consent.__dict__, instance=subject_consent)
        form.is_valid()
        self.assertEqual({}, form._errors)

    @tag("1")
    def test_raises_on_duplicate_identity2(self):
        data = self.cleaned_data()
        data.update(identity="987654321", confirm_identity="987654321")
        form = SubjectConsentForm(data=data, instance=SubjectConsent())
        self.assertTrue(form.is_valid())
        form.save(commit=True)

        form = SubjectConsentForm(data=data, instance=SubjectConsent())
        form.is_valid()
        self.assertIn("identity", form._errors)

    @tag("2")
    def test_raises_on_duplicate_identity3(self):
        # save subject1 with identity="987654321"
        data = self.cleaned_data(last_name="TWO", initials="TT")
        data.update(identity="987654321", confirm_identity="987654321")
        form = SubjectConsentForm(data=data, instance=SubjectConsent())
        self.assertTrue(form.is_valid())
        form.save(commit=True)

        # save subject2 with another identity
        form = SubjectConsentForm(data=self.cleaned_data(), instance=SubjectConsent())
        self.assertTrue(form.is_valid())
        subject_consent2 = form.save(commit=True)

        # try to change subject2 identity to subject1 identity
        subject_consent2.refresh_from_db()
        self.assertEqual(subject_consent2.identity, "12315678")
        data = deepcopy(subject_consent2.__dict__)
        data.update(identity="987654321", confirm_identity="987654321")
        form = SubjectConsentForm(data=data, instance=subject_consent2)
        form.is_valid()
        self.assertIn("identity", form._errors)
