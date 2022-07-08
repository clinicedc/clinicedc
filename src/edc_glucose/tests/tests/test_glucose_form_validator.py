from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_constants.constants import NOT_APPLICABLE, YES
from edc_lab.constants import EQ
from edc_reportable import MILLIMOLES_PER_LITER
from edc_utils import get_utcnow

from edc_glucose.form_validators import GlucoseFormValidator

from ..models import Appointment, SubjectVisit


class TestGlucose(TestCase):
    def setUp(self):
        self.subject_identifier = "1234"
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier, visit_code=1000, visit_code_sequence=0
        )
        self.subject_visit_baseline = SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_identifier,
            visit_code=1000,
            visit_code_sequence=0,
        )
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier, visit_code=2000, visit_code_sequence=0
        )
        self.subject_visit_followup = SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_identifier,
            visit_code=2000,
            visit_code_sequence=0,
        )

    def test_glucose_result(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            def clean(self):
                self.validate_glucose_test()

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_units=MILLIMOLES_PER_LITER,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_date", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_date=get_utcnow().date,
            glucose_units=MILLIMOLES_PER_LITER,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("fasting", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
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
            subject_visit=self.subject_visit_baseline,
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
            subject_visit=self.subject_visit_baseline,
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
            subject_visit=self.subject_visit_baseline,
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
