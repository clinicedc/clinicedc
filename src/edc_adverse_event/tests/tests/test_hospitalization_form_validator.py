from datetime import timedelta

from django import forms
from django.test import TestCase
from edc_constants.constants import NO, NOT_APPLICABLE, UNKNOWN, YES
from edc_form_validators import FormValidatorTestCaseMixin
from edc_form_validators.tests.mixins import FormValidatorTestMixin
from edc_utils import get_utcnow, get_utcnow_as_date

from edc_adverse_event.form_validators import HospitalizationFormValidator as Base


class HospitalizationFormValidator(FormValidatorTestMixin, Base):
    pass


class TestHospitalizationFormValidation(FormValidatorTestCaseMixin, TestCase):
    form_validator_cls = HospitalizationFormValidator

    @staticmethod
    def get_cleaned_data() -> dict:
        return {
            "report_datetime": get_utcnow(),
            "have_details": YES,
            "admitted_date": get_utcnow_as_date() - timedelta(days=3),
            "admitted_date_estimated": NO,
            "discharged": YES,
            "discharged_date": get_utcnow_as_date() - timedelta(days=1),
            "discharged_date_estimated": NO,
            "narrative": "Details of admission",
        }

    def test_cleaned_data_ok(self):
        cleaned_data = self.get_cleaned_data()
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_minimal_details_ok(self):
        cleaned_data = {
            "report_datetime": get_utcnow(),
            "have_details": NO,
            "admitted_date": get_utcnow_as_date(),
            "admitted_date_estimated": NO,
            "discharged": UNKNOWN,
            "discharged_date": None,
            "discharged_date_estimated": NOT_APPLICABLE,
            "narrative": "",
        }
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_discharged_date_required_if_discharged_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date(),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": None,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("discharged_date", cm.exception.error_dict)
        self.assertEqual(
            {"discharged_date": ["This field is required."]},
            cm.exception.message_dict,
        )

    def test_discharged_date_not_required_if_discharged_not_yes(self):
        for answer in [NO, UNKNOWN]:
            with self.subTest(answer=answer):
                cleaned_data = self.get_cleaned_data()
                cleaned_data.update(
                    {
                        "have_details": NO,
                        "admitted_date": get_utcnow_as_date(),
                        "admitted_date_estimated": NO,
                        "discharged": answer,
                        "discharged_date": get_utcnow_as_date(),
                    }
                )
                form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
                with self.assertRaises(forms.ValidationError) as cm:
                    form_validator.validate()
                self.assertIn("discharged_date", cm.exception.error_dict)
                self.assertEqual(
                    {"discharged_date": ["This field is not required."]},
                    cm.exception.message_dict,
                )

    def test_discharged_date_after_admitted_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=1),
                "discharged_date_estimated": NO,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_discharged_date_same_as_admitted_date_ok(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=3),
                "discharged_date_estimated": NO,
                # CSF date cannot be after date discharged
                "csf_positive_cm_date": get_utcnow_as_date() - timedelta(days=3),
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_discharged_date_raises_if_earlier_than_admitted_date(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date() - timedelta(days=3),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date() - timedelta(days=4),
                "discharged_date_estimated": NO,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("discharged_date", cm.exception.error_dict)
        self.assertEqual(
            {"discharged_date": ["Invalid. Cannot be before date admitted."]},
            cm.exception.message_dict,
        )

    def test_discharged_date_estimated_applicable_if_discharged_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "admitted_date": get_utcnow_as_date(),
                "admitted_date_estimated": NO,
                "discharged": YES,
                "discharged_date": get_utcnow_as_date(),
                "discharged_date_estimated": NOT_APPLICABLE,
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("discharged_date_estimated", cm.exception.error_dict)
        self.assertEqual(
            {"discharged_date_estimated": ["This field is applicable."]},
            cm.exception.message_dict,
        )

    def test_discharged_date_estimated_applicable_if_discharged_not_yes(self):
        for answer in [NO, UNKNOWN]:
            with self.subTest(answer=answer):
                cleaned_data = self.get_cleaned_data()
                cleaned_data.update(
                    {
                        "have_details": NO,
                        "admitted_date": get_utcnow_as_date(),
                        "admitted_date_estimated": NO,
                        "discharged": answer,
                        "discharged_date": None,
                        "discharged_date_estimated": "D",
                    }
                )
                form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
                with self.assertRaises(forms.ValidationError) as cm:
                    form_validator.validate()
                self.assertIn("discharged_date_estimated", cm.exception.error_dict)
                self.assertEqual(
                    {"discharged_date_estimated": ["This field is not applicable."]},
                    cm.exception.message_dict,
                )

    def test_narrative_required_if_have_details_yes(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": YES,
                "narrative": "",
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("narrative", cm.exception.error_dict)
        self.assertEqual(
            {"narrative": ["This field is required."]},
            cm.exception.message_dict,
        )

    def test_narrative_can_still_be_entered_if_have_details_no(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "have_details": NO,
                "narrative": "bbbb",
            }
        )
        form_validator = HospitalizationFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")
