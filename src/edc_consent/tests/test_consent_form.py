from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase, tag
from edc_constants.constants import NO, MALE, FEMALE, OMANG
from faker import Faker
from model_mommy import mommy

from ..consent import Consent
from ..modelform_mixins import ConsentModelFormMixin
from ..site_consents import site_consents
from .models import SubjectConsent
from .dates_test_mixin import DatesTestMixin
from pprint import pprint


fake = Faker()


class SubjectConsentForm(ConsentModelFormMixin, forms.ModelForm):
    class Meta:
        model = SubjectConsent
        fields = "__all__"


class TestConsentForm(DatesTestMixin, TestCase):
    def setUp(self):
        site_consents.registry = {}
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

    def consent_factory(self, **kwargs):
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

    def test_base_form_is_valid(self):
        """Asserts mommy defaults validate.
        """
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            dob=self.dob,
            consent_datetime=self.study_open_datetime,
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        consent_form = SubjectConsentForm(data=subject_consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_catches_consent_datetime_before_study_open(self):
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
            dob=self.dob,
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        consent_form = SubjectConsentForm(data=subject_consent.__dict__)
        self.assertTrue(consent_form.is_valid())
        self.assertIsNone(consent_form.errors.get("consent_datetime"))
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime - relativedelta(days=1),
            dob=self.dob,
        )
        data = subject_consent.__dict__
        data["initials"] = data["first_name"][0] + data["last_name"][0]
        consent_form = SubjectConsentForm(data=data)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_identity_mismatch(self):
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        subject_consent.confirm_identity = "1"
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        consent_form = SubjectConsentForm(data=subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_identity_dupl(self):
        mommy.make_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            identity="123156788",
            confirm_identity="123156788",
        )
        consent2 = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            identity="123156788",
            confirm_identity="123156788",
        )
        consent_form = SubjectConsentForm(consent2.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_guardian_and_dob1(self):
        """Asserts form for minor is not valid without guardian name.
        """
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        subject_consent.guardian_name = None
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
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
        """Asserts form for minor is valid with guardian name.
        """
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
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
        """Asserts form for adult is valid.
        """
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
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
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
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
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob + relativedelta(years=25),
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_catches_dob_upper(self):
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob - relativedelta(years=100),
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        consent_form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(consent_form.is_valid())

    def test_base_form_catches_gender_of_consent(self):
        site_consents.registry = {}
        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version="1.0",
            gender=[MALE],
        )
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            gender=MALE,
        )
        form = SubjectConsentForm(subject_consent.__dict__)
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        self.assertTrue(form.is_valid())
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            gender=FEMALE,
        )
        form = SubjectConsentForm(subject_consent.__dict__)
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        self.assertFalse(form.is_valid())

    def test_base_form_catches_is_literate_and_witness(self):
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            is_literate=NO,
            witness_name="",
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        form = SubjectConsentForm(subject_consent.__dict__)
        self.assertFalse(form.is_valid())
        subject_consent = mommy.prepare_recipe(
            "edc_consent.subjectconsent",
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            is_literate=NO,
            witness_name="BOND, JAMES",
        )
        subject_consent.initials = (
            subject_consent.first_name[0] + subject_consent.last_name[0]
        )
        form = SubjectConsentForm(subject_consent.__dict__)
        self.assertTrue(form.is_valid())
