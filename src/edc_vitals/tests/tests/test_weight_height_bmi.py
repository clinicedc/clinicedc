from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_utils import get_utcnow

from edc_vitals.form_validators import WeightHeightBmiFormValidatorMixin

from ..models import WeightHeightBmi


class TestWeightHeightBmi(TestCase):
    def test_allows_none(self):
        obj = WeightHeightBmi()
        obj.save()

        obj = WeightHeightBmi(weight=65.0)
        obj.save()

        obj = WeightHeightBmi(height=65.0)
        obj.save()

    def test_calculates_bmi(self):
        obj = WeightHeightBmi(
            weight=Decimal("65.0"),
            height=Decimal("180.0"),
            dob=get_utcnow() - relativedelta(years=25),
        )
        obj.save()
        self.assertEqual(round(obj.calculated_bmi_value, 4), 20.0617)

    def test_form_validator(self):
        form_validator = WeightHeightBmiFormValidatorMixin()
        form_validator.validate_weight_height_with_bmi()
        cleaned_data = dict(weight=65, height=180)
        form_validator.validate_weight_height_with_bmi(
            weight_kg=cleaned_data.get("weight"),
            height_cm=cleaned_data.get("height"),
        )

        cleaned_data = dict(weight=65, height=18)
        self.assertRaises(
            forms.ValidationError,
            form_validator.validate_weight_height_with_bmi,
            weight_kg=cleaned_data.get("weight"),
            height_cm=cleaned_data.get("height"),
        )

        cleaned_data = dict(weight=65, height=180)
        self.assertRaises(
            forms.ValidationError,
            form_validator.validate_weight_height_with_bmi,
            weight_kg=cleaned_data.get("weight"),
            height_cm=cleaned_data.get("height"),
            dob=get_utcnow() - relativedelta(years=10),
        )

        cleaned_data = dict(weight=65, height=180)
        try:
            form_validator.validate_weight_height_with_bmi(
                weight_kg=cleaned_data.get("weight"),
                height_cm=cleaned_data.get("height"),
                dob=get_utcnow() - relativedelta(years=18),
            )
        except forms.ValidationError as e:
            self.fail(f"forms.ValidationError unexpectedly raised. Got {e}")
