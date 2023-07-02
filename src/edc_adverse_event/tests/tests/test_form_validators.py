from datetime import date

from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_facility import import_holidays
from edc_form_validators import FormValidator

from adverse_event_app.models import DeathReportTmg
from edc_adverse_event.form_validator_mixins import (
    RequiresDeathReportFormValidatorMixin,
)

from .mixins import DeathReportTestMixin


class TestFormValidators(DeathReportTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        super().setUpClass()

    def test_death_report_not_found(self):
        class TestFormValidator(RequiresDeathReportFormValidatorMixin, FormValidator):
            death_date_field = "death_date"

            def clean(self):
                self.match_date_of_death_or_raise()

        data = dict(subject_identifier=self.subject_identifier, death_date=date(2000, 1, 1))
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn("not found", str(form_validator._errors.get("__all__")))

    def test_death_report_found(self):
        class TestFormValidator(RequiresDeathReportFormValidatorMixin, FormValidator):
            death_date_field = "death_date"

            def clean(self):
                self.match_date_of_death_or_raise()

        death_report = self.get_death_report()
        data = dict(
            subject_identifier=self.subject_identifier,
            death_date=death_report.death_datetime.date(),
        )
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)

        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_death_report_date(self):
        class TestFormValidator(RequiresDeathReportFormValidatorMixin, FormValidator):
            death_date_field = "death_date"

            def clean(self):
                self.match_date_of_death_or_raise()

        data = dict(subject_identifier=self.subject_identifier, death_date=None)
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        # specify date of death when there is not death report, raises
        data = dict(subject_identifier=self.subject_identifier, death_date=date(2000, 1, 1))
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn("not found", str(form_validator._errors.get("__all__")))

        # add a death report
        death_report = self.get_death_report()
        # use wrong date of death, raises
        data = dict(
            subject_identifier=self.subject_identifier,
            death_date=death_report.death_datetime.date() - relativedelta(days=1),
        )
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn("Date does not match", str(form_validator._errors.get("death_date")))

        # use correct date of death, ok
        data = dict(
            subject_identifier=self.subject_identifier,
            death_date=death_report.death_datetime.date(),
        )
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        # use correct date of death as datetime, ok
        data = dict(
            subject_identifier=self.subject_identifier,
            death_date=death_report.death_datetime,
        )
        death_report.death_datetime = death_report.death_datetime.date()
        death_report.save()
        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_death_report_date2(self):
        class TestFormValidator(RequiresDeathReportFormValidatorMixin, FormValidator):
            death_date_field = "death_date"

            def clean(self):
                self.match_date_of_death_or_raise()

        # add a death report
        death_report = self.get_death_report()
        death_report.death_date = death_report.death_datetime.date()
        death_report.death_datetime = None
        death_report.save()
        death_report.refresh_from_db()

        data = dict(
            subject_identifier=self.subject_identifier,
            death_date=death_report.death_date,
        )

        form_validator = TestFormValidator(cleaned_data=data, model=DeathReportTmg)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")
