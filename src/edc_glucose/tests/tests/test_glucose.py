from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_constants.constants import DM, NO, NOT_APPLICABLE, YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_dx_review.utils import (
    raise_if_clinical_review_does_not_exist,
    raise_if_initial_review_does_not_exist,
)
from edc_form_validators import FormValidator
from edc_lab.constants import EQ
from edc_reportable import MILLIMOLES_PER_LITER
from edc_test_utils.get_subject_visit import SubjectVisitTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule.utils import raise_if_baseline
from model_bakery import baker

from edc_glucose.form_validators import GlucoseFormValidatorMixin


class GlucoseFormValidator(
    GlucoseFormValidatorMixin,
    CrfFormValidatorMixin,
    FormValidator,
):

    required_at_baseline = True
    require_diagnosis = False

    def clean(self):

        if self.cleaned_data.get("subject_visit"):
            if not self.required_at_baseline:
                raise_if_baseline(self.cleaned_data.get("subject_visit"))
            raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
            if self.require_diagnosis:
                raise_if_initial_review_does_not_exist(
                    self.cleaned_data.get("subject_visit"), DM
                )
            self.validate_glucose_test()


class TestGlucose(SubjectVisitTestCaseMixin, TestCase):
    def test_requirement_at_baseline(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = False

        subject_visit_baseline = self.get_subject_visit()

        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=NO,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        e = cm.exception
        self.assertEqual(e.message, "This form is not available for completion at baseline.")

    def test_not_required_at_baseline(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = True

        subject_visit_baseline = self.get_subject_visit()

        cleaned_data = dict(subject_visit=subject_visit_baseline, glucose_performed=NO)
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        e = cm.exception
        self.assertNotEqual(
            e.message, "This form is not available for completion at baseline."
        )

    def test_requires_clinical_initial_review_at_baseline(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = True

        subject_visit_baseline = self.get_subject_visit()
        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=NO,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)

        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertEqual(
            cm.exception.message, "Complete the `Clinical Review: Baseline` CRF first."
        )

        baker.make(
            "respond_test_app.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            dm_test=YES,
            dm_dx=YES,
            dm_test_ago="5y",
        )

        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexceptedly raised")

    def test_requires_clinical_review_at_followup(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = True

        subject_visit_baseline = self.get_subject_visit()
        baker.make(
            "respond_test_app.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            dm_test=YES,
            dm_dx=YES,
            dm_test_ago="5y",
        )

        subject_visit_followup = self.get_next_subject_visit(subject_visit_baseline)
        cleaned_data = dict(
            subject_visit=subject_visit_followup,
            glucose_performed=NO,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)

        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        e = cm.exception
        self.assertEqual(e.message, "Complete the `Clinical Review` CRF first.")

        baker.make(
            "respond_test_app.clinicalreview",
            subject_visit=subject_visit_followup,
        )

        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexceptedly raised")

    def test_requires_diagnosis(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = True
            require_diagnosis = True

        subject_visit_baseline = self.get_subject_visit()
        baker.make(
            "respond_test_app.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            dm_test=YES,
            dm_dx=YES,
            dm_test_ago="5y",
        )
        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=NO,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        e = cm.exception
        self.assertEqual(e.message, "Complete the `Diabetes Initial Review` CRF first.")

        baker.make(
            "respond_test_app.dminitialreview",
            subject_visit=subject_visit_baseline,
            dx_date=subject_visit_baseline.report_datetime,
        )

        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexceptedly raised")

    def test_diagnosis_not_required(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = True
            require_diagnosis = False

        subject_visit_baseline = self.get_subject_visit()
        baker.make(
            "respond_test_app.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            dm_test=YES,
            dm_dx=YES,
            dm_test_ago="5y",
        )
        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=NO,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexceptedly raised")

    def test_glucose_result(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            required_at_baseline = True
            require_diagnosis = False

        subject_visit_baseline = self.get_subject_visit()
        baker.make(
            "respond_test_app.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            dm_test=YES,
            dm_dx=YES,
            dm_test_ago="5y",
        )
        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=YES,
            glucose_units=MILLIMOLES_PER_LITER,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_date", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=YES,
            glucose_date=get_utcnow().date,
            glucose_units=MILLIMOLES_PER_LITER,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("fasting", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=YES,
            glucose_date=get_utcnow().date,
            fasting=YES,
            glucose_units=MILLIMOLES_PER_LITER,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_value", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=YES,
            glucose_date=get_utcnow().date,
            fasting=YES,
            glucose_value=5.3,
            glucose_units=MILLIMOLES_PER_LITER,
            glucose_quantifier=None,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_quantifier", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=YES,
            glucose_date=get_utcnow().date,
            fasting=YES,
            glucose_value=5.3,
            glucose_units=NOT_APPLICABLE,
            glucose_quantifier=EQ,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_units", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=subject_visit_baseline,
            glucose_performed=YES,
            glucose_date=get_utcnow().date,
            fasting=YES,
            glucose_value=5.3,
            glucose_units=MILLIMOLES_PER_LITER,
            glucose_quantifier=EQ,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexceptedly raised")
