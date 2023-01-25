from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import HeartRate


class TestTemperature(TestCase):
    def test_simple_ok(self):
        obj = HeartRate(heart_rate=45)
        obj.save()
        self.assertEqual(obj.heart_rate, 45)

    def test_heart_rate_lt_30_raises(self):
        for low_hr in [0, 1, 28, 29]:
            with self.subTest(heart_rate=low_hr):
                model = HeartRate.objects.create(heart_rate=low_hr)
                with self.assertRaises(ValidationError) as cm:
                    model.full_clean()
                self.assertIn("heart_rate", cm.exception.error_dict)
                self.assertIn(
                    "Ensure this value is greater than or equal to 30.",
                    str(cm.exception.error_dict.get("heart_rate")),
                )

    def test_30_lt_heart_rate_lt_200_ok(self):
        for hr in [30, 31, 45, 60, 120, 199, 200]:
            with self.subTest(heart_rate=hr):
                model = HeartRate.objects.create(heart_rate=hr)
                try:
                    model.full_clean()
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_heart_rate_gt_200_raises(self):
        for high_hr in [201, 202, 300]:
            with self.subTest(heart_rate=high_hr):
                model = HeartRate.objects.create(heart_rate=high_hr)
                with self.assertRaises(ValidationError) as cm:
                    model.full_clean()
                self.assertIn("heart_rate", cm.exception.error_dict)
                self.assertIn(
                    "Ensure this value is less than or equal to 200.",
                    str(cm.exception.error_dict.get("heart_rate")),
                )
