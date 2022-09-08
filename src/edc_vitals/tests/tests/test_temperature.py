from django.core.exceptions import ValidationError
from django.test import TestCase

from edc_vitals.utils import (
    get_g3_fever_lower,
    get_g4_fever_lower,
    has_g3_fever,
    has_g4_fever,
)

from ..models import Temperature


class TestTemperature(TestCase):
    def test_simple_ok(self):
        obj = Temperature(temperature=37.5)
        obj.save()
        self.assertEqual(obj.temperature, 37.5)

    def test_temperature_lt_30_raises(self):
        for low_temp in [28.0, 29, 29.9]:
            with self.subTest(temperature=low_temp):
                model = Temperature.objects.create(temperature=low_temp)
                with self.assertRaises(ValidationError) as cm:
                    model.full_clean()
                self.assertIn("temperature", cm.exception.error_dict)
                self.assertIn(
                    "Ensure this value is greater than or equal to 30.",
                    str(cm.exception.error_dict.get("temperature")),
                )

    def test_30_lt_temperature_lt_45_ok(self):
        for temperature in [30, 31, 37.5, 39.3, 40, 45]:
            with self.subTest(temperature=temperature):
                model = Temperature.objects.create(temperature=temperature)
                try:
                    model.full_clean()
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_temperature_gt_45_raises(self):
        for high_temp in [45.1, 46, 50.0]:
            with self.subTest(temperature=high_temp):
                model = Temperature.objects.create(temperature=high_temp)
                with self.assertRaises(ValidationError) as cm:
                    model.full_clean()
                self.assertIn("temperature", cm.exception.error_dict)
                self.assertIn(
                    "Ensure this value is less than or equal to 45.",
                    str(cm.exception.error_dict.get("temperature")),
                )

    def test_has_fever_passed_none_returns_none(self):
        self.assertIsNone(has_g3_fever())
        self.assertIsNone(has_g4_fever())

    def test_has_g3_fever_returns_false_if_temp_lt_g3(self):
        for temperature in [36, 37, 37.5, 38, 38.6, 39.2]:
            with self.subTest(temperature=temperature):
                self.assertFalse(has_g3_fever(temperature=temperature))

    def test_has_g3_fever_returns_true_if_temp_g3(self):
        for temperature in [39.3, 39.5, 39.9]:
            with self.subTest(temperature=temperature):
                self.assertTrue(has_g3_fever(temperature=temperature))

    def test_has_g3_fever_returns_false_if_temp_gt_g3(self):
        for temperature in [40, 40.1, 41, 45, 50]:
            with self.subTest(temperature=temperature):
                self.assertFalse(has_g3_fever(temperature=temperature))

    def test_has_g4_fever_returns_false_if_temp_lt_g4(self):
        for temperature in [36, 39.2, 39.3, 39.5, 39.9]:
            with self.subTest(temperature=temperature):
                self.assertFalse(has_g4_fever(temperature=temperature))

    def test_has_g4_fever_returns_true_if_temp_g4(self):
        for temperature in [40, 40.1, 41, 45, 50]:
            with self.subTest(temperature=temperature):
                self.assertTrue(has_g4_fever(temperature=temperature))

    def test_get_g3_fever_lower(self):
        self.assertEqual(get_g3_fever_lower(), 39.3)

    def test_get_g4_fever_lower(self):
        self.assertEqual(get_g4_fever_lower(), 40.0)
