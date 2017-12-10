from datetime import datetime
from dateutil.relativedelta import relativedelta
from edc_base.utils import age
from edc_constants.constants import MALE
from pytz import utc
from unittest import TestCase

from ..age_evaluator import AgeEvaluator
from ..evaluator import Evaluator, ValueBoundryError, InvalidUpperBound
from ..evaluator import InvalidCombination, InvalidLowerBound, InvalidUnits
from ..normal_reference import NormalReference


class TestEvaluators(TestCase):

    def test_evaluator(self):
        """Test the basic evaluator.
        """

        ref = Evaluator(
            lower=10,
            upper=100,
            units='mg/dL')
        self.assertTrue(repr(ref))
        self.assertTrue(str(ref))

        self.assertRaises(
            InvalidUnits,
            Evaluator,
            lower=10,
            upper=100,
            units=None)

        ref = Evaluator(
            lower=10,
            upper=100,
            units='mg/dL')
        self.assertRaises(
            ValueBoundryError,
            ref.in_bounds_or_raise, 9, units='mg/dL')
        self.assertRaises(
            ValueBoundryError,
            ref.in_bounds_or_raise, 10, units='mg/dL')
        self.assertTrue(ref.in_bounds_or_raise(11, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(99, units='mg/dL'))
        self.assertRaises(
            ValueBoundryError,
            ref.in_bounds_or_raise, 100, units='mg/dL')
        self.assertRaises(
            ValueBoundryError,
            ref.in_bounds_or_raise, 101, units='mg/dL')

        ref = Evaluator(
            lower=10,
            upper=100,
            units='mg/dL',
            lower_inclusive=True)
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 9, units='mg/dL')
        self.assertTrue(ref.in_bounds_or_raise(10, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(11, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(99, units='mg/dL'))
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 100, units='mg/dL')
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 101, units='mg/dL')

        ref = Evaluator(
            lower=10,
            upper=100,
            units='mg/dL',
            lower_inclusive=True,
            upper_inclusive=True)
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 9, units='mg/dL')
        self.assertTrue(ref.in_bounds_or_raise(10, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(11, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(99, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(100, units='mg/dL'))
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 101, units='mg/dL')

        ref = Evaluator(
            lower=10,
            upper=100,
            units='mg/dL',
            upper_inclusive=True)
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 9, units='mg/dL')
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 10, units='mg/dL')
        self.assertTrue(ref.in_bounds_or_raise(11, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(99, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(100, units='mg/dL'))
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 101, units='mg/dL')

        ref = Evaluator(
            lower=10,
            upper=None,
            units='mg/dL')
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 9, units='mg/dL')
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 10, units='mg/dL')
        self.assertTrue(ref.in_bounds_or_raise(11, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(99, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(100, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(100000000000, units='mg/dL'))

        ref = Evaluator(
            lower=None,
            upper=100,
            units='mg/dL')
        self.assertTrue(ref.in_bounds_or_raise(-1, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(1, units='mg/dL'))
        self.assertTrue(ref.in_bounds_or_raise(99, units='mg/dL'))
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 100, units='mg/dL')
        self.assertRaises(ValueBoundryError,
                          ref.in_bounds_or_raise, 101, units='mg/dL')

        self.assertRaises(
            InvalidUnits, ref.in_bounds_or_raise, 101, units='blah')

        ref = Evaluator(lower=None, upper=100, units='mg/dL')
        self.assertEqual(ref.description(), 'x<100.0 mg/dL')
        self.assertRaises(
            InvalidLowerBound, Evaluator, lower='ERIK', upper=100, units='mg/dL')
        self.assertRaises(
            InvalidUpperBound, Evaluator, lower=10, upper='ERIK', units='mg/dL')
        ref = Evaluator(lower=10, upper=None, units='mg/dL')
        self.assertEqual(ref.description(), '10.0<x mg/dL')

        for lower in [.1, 1.1, 10.2234]:
            with self.subTest(lower=lower):
                try:
                    Evaluator(lower=lower, upper=100, units='mg/dL')
                except InvalidLowerBound:
                    self.fail('InvalidLowerBound unexpectedly raised')

        for upper in [.5, 1.1, 10.2234]:
            with self.subTest(upper=upper):
                try:
                    Evaluator(lower=.1, upper=upper, units='mg/dL')
                except InvalidUpperBound:
                    self.fail('InvalidUpperBound unexpectedly raised')

        self.assertRaises(
            InvalidCombination,
            Evaluator, lower=10, upper=10, units='mg/dL')
        self.assertRaises(
            InvalidCombination,
            Evaluator, lower=11, upper=10, units='mg/dL')

    def test_age_evaluator(self):
        """Test the age evaluator whiich is a child class
        of the basic evaluator.
        """
        report_datetime = utc.localize(datetime(2017, 12, 7))
        dob = report_datetime - relativedelta(years=25)
        rdelta = age(dob, report_datetime)

        self.assertEqual(age(dob, report_datetime).years, 25)
        self.assertTrue(24 < getattr(rdelta, 'years') < 26)
        self.assertFalse(25 < getattr(rdelta, 'years') < 26)
        self.assertFalse(24 < getattr(rdelta, 'years') < 25)

        age_eval = AgeEvaluator(
            age_lower=24,
            age_upper=26)
        self.assertTrue(repr(age_eval))
        self.assertTrue(age_eval.in_bounds_or_raise(dob, report_datetime))

        age_eval = AgeEvaluator(
            age_lower=25,
            age_upper=26)
        self.assertRaises(
            ValueBoundryError,
            age_eval.in_bounds_or_raise, dob, report_datetime)
        age_eval = AgeEvaluator(
            age_lower=24,
            age_upper=25)
        self.assertRaises(
            ValueBoundryError,
            age_eval.in_bounds_or_raise, dob, report_datetime)

    def test_age_match(self):
        """Test age within the NormalReference.
        """
        report_datetime = utc.localize(datetime(2017, 12, 7))
        dob = report_datetime - relativedelta(years=25)

        ref = NormalReference(
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=24,
            age_upper=26,
            gender=MALE)
        self.assertTrue(ref.age_match(dob, report_datetime))

        ref = NormalReference(
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=25,
            age_upper=26,
            gender=MALE)
        self.assertFalse(ref.age_match(dob, report_datetime))

        ref = NormalReference(
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=24,
            age_upper=25,
            gender=MALE)
        self.assertFalse(ref.age_match(dob, report_datetime))
