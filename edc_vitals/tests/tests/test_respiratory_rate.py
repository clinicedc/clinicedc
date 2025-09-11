from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import RespiratoryRate


class TestTemperature(TestCase):
    def test_simple_ok(self):
        obj = RespiratoryRate(respiratory_rate=20)
        obj.save()
        self.assertEqual(obj.respiratory_rate, 20)

    def test_respiratory_rate_lt_6_raises(self):
        for low_rr in [0, 1, 5]:
            with self.subTest(respiratory_rate=low_rr):
                model = RespiratoryRate.objects.create(respiratory_rate=low_rr)
                with self.assertRaises(ValidationError) as cm:
                    model.full_clean()
                self.assertIn("respiratory_rate", cm.exception.error_dict)
                self.assertIn(
                    "Ensure this value is greater than or equal to 6.",
                    str(cm.exception.error_dict.get("respiratory_rate")),
                )

    def test_6_lt_respiratory_rate_lt_50_ok(self):
        for rr in [6, 7, 10, 20, 49, 50]:
            with self.subTest(respiratory_rate=rr):
                model = RespiratoryRate.objects.create(respiratory_rate=rr)
                try:
                    model.full_clean()
                except ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_respiratory_rate_gt_50_raises(self):
        for high_rr in [51, 52, 60, 100]:
            with self.subTest(respiratory_rate=high_rr):
                model = RespiratoryRate.objects.create(respiratory_rate=high_rr)
                with self.assertRaises(ValidationError) as cm:
                    model.full_clean()
                self.assertIn("respiratory_rate", cm.exception.error_dict)
                self.assertIn(
                    "Ensure this value is less than or equal to 50.",
                    str(cm.exception.error_dict.get("respiratory_rate")),
                )
