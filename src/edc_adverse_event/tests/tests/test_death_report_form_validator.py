from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_constants.constants import OTHER, UNKNOWN
from edc_constants.disease_constants import BACTERAEMIA
from edc_form_validators import FormValidatorTestCaseMixin
from edc_form_validators.tests.mixins import FormValidatorTestMixin
from edc_utils import get_utcnow

from edc_adverse_event.form_validators import DeathReportFormValidator as Base


class DeathReportFormValidator(FormValidatorTestMixin, Base):
    pass


class TestHospitalizationFormValidation(FormValidatorTestCaseMixin, TestCase):
    @staticmethod
    def get_cleaned_data() -> dict:
        report_datetime = get_utcnow()
        return {
            "report_datetime": report_datetime,
            "death_datetime": report_datetime - relativedelta(days=3),
            "cause_of_death": BACTERAEMIA,
            "cause_of_death_other": "",
            "narrative": "Narrative around death",
        }

    def test_cleaned_data_ok(self):
        cleaned_data = self.get_cleaned_data()
        form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_death_datetime_after_report_datetime_raises(self):
        for death_report_date_field in ["death_date", "death_datetime"]:
            for days_after in [1, 3, 14]:
                with self.subTest(
                    death_report_date_field=death_report_date_field, days_after=days_after
                ):
                    report_datetime = get_utcnow()
                    death_datetime = report_datetime + relativedelta(days=days_after)
                    cleaned_data = {
                        "report_datetime": get_utcnow(),
                        death_report_date_field: (
                            death_datetime
                            if death_report_date_field == "death_datetime"
                            else death_datetime.date()
                        ),
                    }
                    form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
                    form_validator.death_report_date_field = death_report_date_field
                    with self.assertRaises(forms.ValidationError) as cm:
                        form_validator.validate()
                    self.assertIn("report_datetime", cm.exception.error_dict)
                    self.assertIn(
                        "Invalid. Expected a date on or after",
                        str(cm.exception.error_dict.get("report_datetime")),
                    )
                    self.assertIn(
                        "(on or after date of death)",
                        str(cm.exception.error_dict.get("report_datetime")),
                    )

    def test_death_datetime_on_or_before_report_datetime_datetime_ok(self):
        for death_report_date_field in ["death_date", "death_datetime"]:
            for days_before in [0, 1, 2, 14]:
                with self.subTest(
                    death_report_date_field=death_report_date_field, days_before=days_before
                ):
                    report_datetime = get_utcnow()
                    death_datetime = report_datetime - relativedelta(days=days_before)
                    cleaned_data = {
                        "report_datetime": report_datetime,
                        death_report_date_field: death_datetime
                        if death_report_date_field == "death_datetime"
                        else death_datetime.date(),
                    }
                    form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
                    form_validator.death_report_date_field = death_report_date_field
                    try:
                        form_validator.validate()
                    except forms.ValidationError as e:
                        self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_cause_of_death_other_required_if_cause_of_death_other(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "cause_of_death": OTHER,
                "cause_of_death_other": "",
            }
        )
        form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cause_of_death_other", cm.exception.error_dict)
        self.assertIn(
            "This field is required.",
            str(cm.exception.error_dict.get("cause_of_death_other")),
        )

        cleaned_data.update({"cause_of_death_other": "Some other cause of death..."})
        form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_cause_of_death_other_not_required_if_cause_of_death_not_other(self):
        cleaned_data = self.get_cleaned_data()
        cleaned_data.update(
            {
                "cause_of_death": UNKNOWN,
                "cause_of_death_other": "Some other cause of death",
            }
        )
        form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("cause_of_death_other", cm.exception.error_dict)
        self.assertIn(
            "This field is not required.",
            str(cm.exception.error_dict.get("cause_of_death_other")),
        )

        cleaned_data.update({"cause_of_death_other": ""})
        form_validator = DeathReportFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")
