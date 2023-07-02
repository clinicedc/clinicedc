from datetime import timedelta
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.sites.models import Site
from django.forms import model_to_dict
from django.test import TestCase, override_settings
from edc_constants.constants import FEMALE, MALE, NO, NOT_APPLICABLE, YES
from edc_crf.crf_form_validator_mixins import BaseFormValidatorMixin
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_protocol import Protocol
from edc_utils import age, get_utcnow
from faker import Faker
from model_bakery import baker

from edc_consent.consent import Consent
from edc_consent.modelform_mixins import ConsentModelFormMixin
from edc_consent.site_consents import site_consents

from ...form_validators import SubjectConsentFormValidatorMixin
from ..models import SubjectConsent, SubjectScreening

fake = Faker()


class SubjectConsentFormValidator(
    SubjectConsentFormValidatorMixin, BaseFormValidatorMixin, FormValidator
):
    pass


class SubjectConsentForm(ConsentModelFormMixin, FormValidatorMixin, forms.ModelForm):
    form_validator_cls = SubjectConsentFormValidator

    screening_identifier = forms.CharField(
        label="Screening identifier",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = SubjectConsent
        fields = "__all__"


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
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

    def prepare_subject_consent(
        self,
        dob=None,
        consent_datetime=None,
        first_name=None,
        last_name=None,
        initials=None,
        gender=None,
        screening_identifier=None,
        identity=None,
        confirm_identity=None,
        age_in_years=None,
        is_literate=None,
        witness_name=None,
        create_subject_screening=None,
    ):
        create_subject_screening = (
            True if create_subject_screening is None else create_subject_screening
        )
        consent_datetime = consent_datetime or self.study_open_datetime
        dob = dob or self.study_open_datetime - relativedelta(years=25)
        gender = gender or FEMALE
        screening_identifier = screening_identifier or "ABCD"
        age_in_years = age_in_years or age(dob, reference_dt=consent_datetime).years
        initials = initials or "XX"
        if create_subject_screening:
            SubjectScreening.objects.create(
                age_in_years=age_in_years,
                initials=initials,
                gender=gender,
                screening_identifier=screening_identifier,
                report_datetime=consent_datetime,
                eligible=True,
                eligibility_datetime=consent_datetime,
            )
        subject_consent = baker.prepare_recipe(
            "edc_consent.subjectconsent",
            dob=dob,
            consent_datetime=consent_datetime,
            first_name=first_name or "XXXXXX",
            last_name=last_name or "XXXXXX",
            initials=initials,
            gender=gender,
            identity=identity or "123456789",
            confirm_identity=confirm_identity or "123456789",
            screening_identifier=screening_identifier,
            is_literate=is_literate or YES,
            witness_name=witness_name,
        )
        return subject_consent

    def test_base_form_is_valid(self):
        """Asserts baker defaults validate."""
        options = dict(
            dob=self.dob,
            consent_datetime=self.study_open_datetime,
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        self.assertTrue(form.is_valid())

    def test_base_form_catches_consent_datetime_before_study_open(self):
        options = dict(
            consent_datetime=self.study_open_datetime + relativedelta(days=1),
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertEqual(form._errors, {})

        # change consent_datetime to before the consent period
        options.update(consent_datetime=self.study_open_datetime - relativedelta(days=1))
        subject_consent = self.prepare_subject_consent(
            **options, create_subject_screening=False
        )
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("consent_datetime", form._errors)

    def test_base_form_identity_mismatch(self):
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
            identity="1",
            confirm_identity="2",
        )
        subject_consent = self.prepare_subject_consent(**options)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("identity", form._errors)

    def test_base_form_identity_dupl(self):
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        subject_consent.save()

        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.dob,
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK2",
            last_name="THEPLEEB2",
            initials="ET",
            screening_identifier="ABCD1XXX",
        )
        subject_consent = self.prepare_subject_consent(**options)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("identity", form._errors)

    def test_base_form_guardian_and_dob1(self):
        """Asserts form for minor is not valid without guardian name."""
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=16),
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        subject_consent.guardian_name = None
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("guardian_name", form._errors)

    def test_base_form_guardian_and_dob2(self):
        """Asserts form for minor is valid with guardian name."""
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=16),
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        subject_consent.guardian_name = "SPOCK, YOUCOULDNTPRONOUNCEIT"
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_base_form_guardian_and_dob4(self):
        """Asserts form for adult is not valid if guardian name
        specified.
        """
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=25),
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        subject_consent.guardian_name = "SPOCK, YOUCOULDNTPRONOUNCEIT"
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("guardian_name", form._errors)

    def test_base_form_catches_dob_lower(self):
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=15),
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("dob", form._errors)

    def test_base_form_catches_dob_upper(self):
        options = dict(
            consent_datetime=self.study_open_datetime,
            dob=self.study_open_datetime - relativedelta(years=100),
            identity="123156788",
            confirm_identity="123156788",
            first_name="ERIK",
            last_name="THEPLEEB",
            initials="ET",
            screening_identifier="ABCD1",
        )
        subject_consent = self.prepare_subject_consent(**options)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("dob", form._errors)

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
        subject_consent = self.prepare_subject_consent(gender=MALE)
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertEqual({}, form._errors)

        subject_consent = self.prepare_subject_consent(
            gender=FEMALE, create_subject_screening=False
        )
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("gender", form._errors)

    def test_base_form_catches_is_literate_and_witness(self):
        subject_consent = self.prepare_subject_consent(
            is_literate=NO,
            witness_name="",
        )
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertIn("witness_name", form._errors)

        subject_consent = self.prepare_subject_consent(
            is_literate=NO,
            witness_name="BUBBA, BUBBA",
            create_subject_screening=False,
        )
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_raises_on_duplicate_identity1(self):
        subject_consent = self.prepare_subject_consent(
            identity="1", confirm_identity="1", screening_identifier="LOPIKKKK"
        )
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier=data.get("screening_identifier")),
            instance=SubjectConsent(),
        )
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save(commit=True)

        subject_consent = self.prepare_subject_consent(
            identity="1", confirm_identity="1", screening_identifier="LOPIKXSWE"
        )
        opts = SubjectConsentForm._meta
        data = model_to_dict(subject_consent, opts.fields, opts.exclude)
        form = SubjectConsentForm(
            data=data,
            initial=dict(screening_identifier="LOPIKXSWE"),
            instance=subject_consent,
        )
        form.is_valid()
        self.assertIn("identity", form._errors)
