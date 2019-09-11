from django.test import TestCase, tag
from edc_reportable.evaluator import ValueBoundryError

from ..age_evaluator import AgeEvaluator


class TestEvaluators(TestCase):
    def test_age(self):
        evaluator = AgeEvaluator(age_lower=18, age_lower_inclusive=True)

        self.assertRaises(ValueBoundryError, evaluator.in_bounds_or_raise, age=17)
