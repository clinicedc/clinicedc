from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from django.forms import model_to_dict
from django.test import override_settings, tag, TestCase
from faker import Faker
from model_bakery import baker

from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE, NO, NOT_APPLICABLE, SUBJECT, YES
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_utils import age, get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from tests.consents import consent1_v1, consent1_v2, consent1_v3
from tests.forms import SubjectConsentForm, SubjectConsentFormValidator
from tests.helper import Helper
from tests.models import (
    SubjectConsentV1,
    SubjectScreening,
)
from tests.sites import all_sites
from tests.visit_schedules.visit_schedule_consent import get_visit_schedule

fake = Faker()


@tag("consent")
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(EDC_AUTH_SKIP_AUTH_UPDATER=False, SITE_ID=10)
class TestConsentForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime

        site_consents.registry = {}
        site_consents.register(consent1_v1)
        site_consents.register(consent1_v2, updated_by=consent1_v3)
        site_consents.register(consent1_v3)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(
            get_visit_schedule([consent1_v1, consent1_v2, consent1_v3])
        )

        self.dob = self.study_open_datetime - relativedelta(years=25)

    @staticmethod
    def get_mock_screening(subject_consent=None, **kwargs):
        mock_subject_screening = Mock()
        mock_subject_screening.eligible = YES
        mock_subject_screening.eligibility_datetime = (
            subject_consent.consent_datetime - relativedelta(minutes=1)
        )
        mock_subject_screening.age_in_years = 25
        mock_subject_screening.report_datetime = (
            subject_consent.consent_datetime - relativedelta(minutes=1)
        )
        mock_subject_screening.gender = subject_consent.gender
        for k, v in kwargs.items():
            setattr(mock_subject_screening, k, v)
        return mock_subject_screening

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
        guardian_name=None,
    ):
        create_subject_screening = (
            True if create_subject_screening is None else create_subject_screening
        )
        consent_datetime = consent_datetime or self.study_open_datetime
        dob = dob or self.study_open_datetime - relativedelta(years=25)
        gender = gender or FEMALE
        age_in_years = age_in_years or age(dob, reference_dt=consent_datetime).years
        initials = initials or "XX"
        if create_subject_screening:
            subject_screening = SubjectScreening.objects.create(
                age_in_years=age_in_years,
                initials=initials,
                gender=gender,
                report_datetime=consent_datetime,
                eligible=True,
                eligibility_datetime=consent_datetime,
            )
            screening_identifier = subject_screening.screening_identifier
        subject_consent = baker.prepare_recipe(
            "tests.subjectconsentv1",
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
            guardian_name=guardian_name,
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
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=consent1_v1,
            dob=self.study_open_datetime - relativedelta(years=25),
            guardian_name="",
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    # initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=subject_consent,
                )
                self.assertTrue(form.is_valid())

    def test_base_form_catches_consent_datetime_before_study_open(self):
        helper = Helper()
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=consent1_v1,
            dob=self.study_open_datetime - relativedelta(years=25),
            guardian_name="",
            report_datetime=get_utcnow(),
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                data.update(citizen=YES, is_dob_estimated="-", subject_type=SUBJECT)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=subject_consent,
                )
                form.is_valid()
                mock_is_eligible.assert_called_once()
                self.assertEqual(form._errors, {})
        traveller.stop()

        traveller = time_machine.travel(
            self.study_open_datetime - relativedelta(days=1)
        )
        traveller.start()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=consent1_v1,
            dob=self.study_open_datetime - relativedelta(years=25),
            guardian_name="",
        )

        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch("edc_screening.utils.is_eligible_or_raise") as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=SubjectConsentV1(site=subject_consent.site),
                )
                form.is_valid()
                self.assertIn("consent_datetime", form._errors)
        traveller.stop()

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
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=SubjectConsentV1(site=subject_consent.site),
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
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=SubjectConsentV1(site=subject_consent.site),
                )
                form.is_valid()
                self.assertIn("identity", form._errors)

    def test_base_form_guardian_and_dob1(self):
        """Asserts form for minor is not valid without guardian name."""

        # can't get to this with an invalid age
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=consent1_v1,
            dob=self.study_open_datetime - relativedelta(years=25),
            guardian_name="",
        )

        mock_subject_screening = Mock()
        mock_subject_screening.eligibility_datetime = (
            subject_consent.consent_datetime - relativedelta(minutes=1)
        )
        mock_subject_screening.age_in_years = 25
        mock_subject_screening.report_datetime = (
            subject_consent.consent_datetime - relativedelta(minutes=1)
        )
        with patch.object(
            SubjectConsentFormValidator, "subject_screening", new=mock_subject_screening
        ):
            data = model_to_dict(subject_consent)
            # try to change the dob
            data.update(
                dob=self.study_open_datetime - relativedelta(years=15),
                citizen=YES,
                is_dob_estimated="-",
                subject_type=SUBJECT,
                consent_reviewed=YES,
                study_questions=YES,
                assessment_score=YES,
                consent_signature=YES,
                consent_copy=YES,
                is_incarcerated=NO,
                language="en",
            )
            form = SubjectConsentForm(
                data=data,
                initial=dict(screening_identifier=data.get("screening_identifier")),
                instance=SubjectConsentForm._meta.model(site=subject_consent.site),
            )
            form.is_valid()
            self.assertIn("dob", form._errors)  # Age mismatch with screening

    def test_base_form_guardian_and_dob2(self):
        """Asserts form for minor is valid with guardian name."""
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=consent1_v1,
            dob=self.study_open_datetime - relativedelta(years=16),
            guardian_name="SPOCK, YOUCOULDNTPRONOUNCEIT",
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=SubjectConsentForm._meta.model(site=subject_consent.site),
                )
                form.is_valid()
                self.assertNotIn("guardian_name", form._errors)

    def test_base_form_guardian_and_dob4(self):
        """Asserts form for adult is not valid if guardian name
        specified.
        """
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            consent_definition=consent1_v1,
            dob=self.study_open_datetime - relativedelta(years=25),
            guardian_name="SPOCK, YOUCOULDNTPRONOUNCEIT",
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=SubjectConsentForm._meta.model(site=subject_consent.site),
                )
                form.is_valid()
                self.assertIn("guardian_name", form._errors)

    def test_base_form_catches_dob_upper(self):
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
            dob=self.study_open_datetime - relativedelta(years=110),
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                data["dob"] = self.study_open_datetime.date() - relativedelta(years=100)
                form = SubjectConsentForm(
                    data=data,
                    instance=subject_consent,
                )
                form.is_valid()
                self.assertIn("dob", form._errors)

    def test_base_form_catches_gender_of_consent(self):
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule1",
        )
        data = model_to_dict(subject_consent)
        data["gender"] = "UNDEFINED"
        form = SubjectConsentForm(
            data=data,
            instance=subject_consent,
        )
        form.is_valid()
        self.assertIn("gender", form._errors)

    def test_base_form_catches_is_literate_and_witness(self):
        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule1"
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                data["is_literate"] = NO
                data["witness_name"] = ""
                form = SubjectConsentForm(
                    data=data,
                    instance=subject_consent,
                )
                form.is_valid()
                self.assertIn("witness_name", form._errors)

                data["is_literate"] = NO
                data["witness_name"] = "BUBBA, SHRIMP"
                form = SubjectConsentForm(
                    data=data,
                    instance=subject_consent,
                )
                form.is_valid()
                self.assertNotIn("witness_name", form._errors)

    def test_raises_on_duplicate_identity1(self):
        subject_consent = self.prepare_subject_consent(
            identity="1", confirm_identity="1", screening_identifier="LOPIKKKK"
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier=data.get("screening_identifier")),
                    instance=subject_consent,
                )
                form.is_valid()
                self.assertEqual({}, form._errors)
                form.save(commit=True)

        subject_consent = self.prepare_subject_consent(
            identity="1", confirm_identity="1", screening_identifier="LOPIKXSWE"
        )
        mock_subject_screening = self.get_mock_screening(subject_consent)
        with patch(
            "edc_consent.modelform_mixins.consent_modelform_mixin."
            "ConsentModelFormMixin.validate_is_eligible_or_raise"
        ) as mock_is_eligible:
            mock_is_eligible.return_value = None
            with patch.object(
                SubjectConsentFormValidator,
                "subject_screening",
                new=mock_subject_screening,
            ):
                data = model_to_dict(subject_consent)
                form = SubjectConsentForm(
                    data=data,
                    initial=dict(screening_identifier="LOPIKXSWE"),
                    instance=subject_consent,
                )
                form.is_valid()
                self.assertIn("identity", form._errors)
