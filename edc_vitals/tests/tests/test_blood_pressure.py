from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_constants.constants import YES

from edc_vitals.form_validators import BloodPressureFormValidatorMixin
from edc_vitals.utils import has_severe_htn

from ..models import BloodPressure, SimpleBloodPressure


class TestBloodPressure(TestCase):
    def test_allows_none(self):
        obj = BloodPressure()
        obj.save()

    def test_calculates_avg_only_if_fields_provided(self):
        obj = BloodPressure(sys_blood_pressure_one=100)
        obj.save()
        obj.refresh_from_db()
        self.assertIsNone(obj.sys_blood_pressure_avg, obj.dia_blood_pressure_avg)

        obj = BloodPressure(sys_blood_pressure_one=100, dia_blood_pressure_one=100)
        obj.save()
        obj.refresh_from_db()
        self.assertIsNone(obj.sys_blood_pressure_avg, obj.dia_blood_pressure_avg)

        obj = BloodPressure(
            sys_blood_pressure_one=100,
            dia_blood_pressure_one=100,
            sys_blood_pressure_two=100,
            dia_blood_pressure_two=100,
        )
        obj.save()
        obj.refresh_from_db()
        self.assertEqual(obj.sys_blood_pressure_avg, 100)
        self.assertEqual(obj.dia_blood_pressure_avg, 100)

    def test_calculates_avg(self):
        obj = BloodPressure(
            sys_blood_pressure_one=110,
            dia_blood_pressure_one=80,
            sys_blood_pressure_two=128,
            dia_blood_pressure_two=91,
        )
        obj.save()
        obj.refresh_from_db()
        self.assertEqual(obj.sys_blood_pressure_avg, 119)
        self.assertEqual(obj.dia_blood_pressure_avg, 85)

    def test_simple_allows_none(self):
        obj = SimpleBloodPressure()
        obj.save()

    def test_simple_ok(self):
        obj = SimpleBloodPressure(
            sys_blood_pressure=110,
            dia_blood_pressure=80,
        )
        obj.save()

    def test_has_severe_htn(self):
        self.assertIsNone(has_severe_htn())
        self.assertIsNone(has_severe_htn(sys=120))
        self.assertFalse(has_severe_htn(sys=120, dia=80))
        self.assertFalse(has_severe_htn(sys=179, dia=109))
        self.assertTrue(has_severe_htn(sys=180, dia=109))
        self.assertTrue(has_severe_htn(sys=179, dia=110))
        self.assertTrue(has_severe_htn(sys=180, dia=110))


class TestBloodPressureFormValidatorMixin(TestCase):
    def test_bp_suggest_severe_htn_form_validator(self):
        cleaned_data = dict(
            sys_blood_pressure_one=None,
            sys_blood_pressure_two=None,
            dia_blood_pressure_one=None,
            dia_blood_pressure_two=None,
        )
        form_validator = BloodPressureFormValidatorMixin()
        self.assertIsNone(
            form_validator.raise_on_avg_blood_pressure_suggests_severe_htn(**cleaned_data)
        )
        cleaned_data.update(sys_blood_pressure_one=180, dia_blood_pressure_one=None)
        self.assertIsNone(
            form_validator.raise_on_avg_blood_pressure_suggests_severe_htn(**cleaned_data)
        )
        cleaned_data.update(sys_blood_pressure_one=180, dia_blood_pressure_one=120)
        self.assertIsNone(
            form_validator.raise_on_avg_blood_pressure_suggests_severe_htn(**cleaned_data)
        )
        cleaned_data.update(
            sys_blood_pressure_one=180,
            dia_blood_pressure_one=120,
            sys_blood_pressure_two=191,
            dia_blood_pressure_two=125,
        )
        self.assertRaises(
            forms.ValidationError,
            form_validator.raise_on_avg_blood_pressure_suggests_severe_htn,
            **cleaned_data,
        )

        cleaned_data.update(severe_htn=YES)
        try:
            form_validator.raise_on_avg_blood_pressure_suggests_severe_htn(**cleaned_data)
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_sys_lt_dia_bp_raises(self):
        cleaned_data = dict(
            sys_blood_pressure=80,
            dia_blood_pressure=120,
        )
        form_validator = BloodPressureFormValidatorMixin()

        with self.assertRaises(ValidationError) as cm:
            form_validator.raise_on_systolic_lt_diastolic_bp(**cleaned_data)
        self.assertIn("dia_blood_pressure", cm.exception.error_dict)
        self.assertIn(
            "Invalid. Diastolic must be less than systolic.",
            str(cm.exception.error_dict.get("dia_blood_pressure")),
        )

        cleaned_data = dict(
            custom_sys_blood_pressure_fld=80,
            custom_dia_blood_pressure_fld=120,
        )
        form_validator = BloodPressureFormValidatorMixin()

        with self.assertRaises(ValidationError) as cm:
            form_validator.raise_on_systolic_lt_diastolic_bp(
                sys_field="custom_sys_blood_pressure_fld",
                dia_field="custom_dia_blood_pressure_fld",
                **cleaned_data,
            )
        self.assertIn("custom_dia_blood_pressure_fld", cm.exception.error_dict)
        self.assertIn(
            "Invalid. Diastolic must be less than systolic.",
            str(cm.exception.error_dict.get("custom_dia_blood_pressure_fld")),
        )

    def test_sys_gte_dia_bp_ok(self):
        for sys, dia in [(120, 80), (180, 110), (100, 99), (90, 90)]:
            with self.subTest(sys=sys, dia=dia):
                cleaned_data = dict(
                    sys_blood_pressure=sys,
                    dia_blood_pressure=dia,
                )
                form_validator = BloodPressureFormValidatorMixin()
                try:
                    form_validator.raise_on_systolic_lt_diastolic_bp(**cleaned_data)
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

                cleaned_data = dict(
                    custom_sys_blood_pressure_fld=sys,
                    custom_dia_blood_pressure_fld=dia,
                )
                try:
                    form_validator.raise_on_systolic_lt_diastolic_bp(
                        sys_field="custom_sys_blood_pressure_fld",
                        dia_field="custom_dia_blood_pressure_fld",
                        **cleaned_data,
                    )
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_raise_on_systolic_lt_diastolic_bp_with_none_ok(self):
        for sys, dia in [(None, None), (None, 80), (120, None)]:
            with self.subTest(sys=sys, dia=dia):
                cleaned_data = dict(
                    sys_blood_pressure=sys,
                    dia_blood_pressure=dia,
                )
                form_validator = BloodPressureFormValidatorMixin()
                try:
                    form_validator.raise_on_systolic_lt_diastolic_bp(**cleaned_data)
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

                cleaned_data = dict(
                    custom_sys_blood_pressure_fld=sys,
                    custom_dia_blood_pressure_fld=dia,
                )
                try:
                    form_validator.raise_on_systolic_lt_diastolic_bp(
                        sys_field="custom_sys_blood_pressure_fld",
                        dia_field="custom_dia_blood_pressure_fld",
                        **cleaned_data,
                    )
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")
