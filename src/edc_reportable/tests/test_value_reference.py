from datetime import datetime
from dateutil.relativedelta import relativedelta
from edc_base.utils import get_utcnow, age
from edc_constants.constants import MALE, FEMALE
from pytz import utc
from unittest import TestCase

from ..age_evaluator import AgeEvaluator
from ..evaluator import Evaluator, ValueBoundryError, InvalidUpperBound
from ..evaluator import InvalidCombination, InvalidLowerBound, InvalidUnits
from ..value_reference import ValueReference
from ..value_reference_group import ValueReferenceGroup, ValueReferenceAlreadyAdded
from ..value_reference_group import InvalidValueReference
from edc_reportable.grade_reference import GradeReference
from pprint import pprint


class TestValueReference(TestCase):

    def test_evaluator(self):

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
        self.assertEqual(ref.description(), 'x<100 in mg/dL')
        self.assertRaises(
            InvalidLowerBound, Evaluator, lower='ERIK', upper=100, units='mg/dL')
        self.assertRaises(
            InvalidUpperBound, Evaluator, lower=10, upper='ERIK', units='mg/dL')
        ref = Evaluator(lower=10, upper=None, units='mg/dL')
        self.assertEqual(ref.description(), '10<x in mg/dL')

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
        report_datetime = utc.localize(datetime(2017, 12, 7))
        dob = report_datetime - relativedelta(years=25)
        rdelta = age(dob, report_datetime)
        self.assertEqual(age(dob, report_datetime).years, 25)
        self.assertTrue(24 < getattr(rdelta, 'years') < 26)
        self.assertFalse(25 < getattr(rdelta, 'years') < 26)
        self.assertFalse(24 < getattr(rdelta, 'years') < 25)
        ref = ValueReference(
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=24,
            age_upper=26,
            gender=MALE)
        self.assertTrue(ref.age_match(dob, report_datetime))
        ref = ValueReference(
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=25,
            age_upper=26,
            gender=MALE)
        self.assertFalse(ref.age_match(dob, report_datetime))
        ref = ValueReference(
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=24,
            age_upper=25,
            gender=MALE)
        self.assertFalse(ref.age_match(dob, report_datetime))

    def test_value_reference_group(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = utc.localize(datetime(2017, 12, 7))
        grp = ValueReferenceGroup(name='labtest')
        self.assertTrue(repr(grp))

        ref = ValueReference(
            name='blahblah',
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)
        self.assertRaises(
            InvalidValueReference,
            grp.add_normal, value_reference=ref)

        ref = ValueReference(
            name='labtest',
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)
        grp.add_normal(value_reference=ref)
        self.assertFalse(grp.in_bounds(
            value=9,
            units='mg/dL',
            gender=MALE,
            dob=dob))
        self.assertFalse(grp.in_bounds(
            value=10,
            units='mg/dL',
            gender=MALE,
            dob=dob))
        self.assertTrue(grp.in_bounds(
            value=11,
            units='mg/dL',
            gender=MALE,
            dob=dob))
        self.assertRaises(
            ValueReferenceAlreadyAdded,
            grp.add_normal, value_reference=ref)

        grp = ValueReferenceGroup(name='labtest')
        ref_male = ValueReference(
            name='labtest',
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)
        ref_female1 = ValueReference(
            name='labtest',
            lower=1.7,
            upper=3.5,
            upper_inclusive=True,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=FEMALE)
        ref_female2 = ValueReference(
            name='labtest',
            lower=7.3,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=FEMALE)
        grp.add_normal(value_reference=ref_male)
        grp.add_normal(value_reference=ref_female1)
        grp.add_normal(value_reference=ref_female2)

        self.assertFalse(grp.in_bounds(
            value=9, gender=MALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertFalse(grp.in_bounds(
            value=10, gender=MALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.in_bounds(
            value=11, gender=MALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))

        self.assertFalse(grp.in_bounds(
            value=1, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertFalse(grp.in_bounds(
            value=1.7, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.in_bounds(
            value=1.8, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.in_bounds(
            value=3.4, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.in_bounds(
            value=3.5, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertFalse(grp.in_bounds(
            value=3.6, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))

        self.assertFalse(grp.in_bounds(
            value=7.3, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.in_bounds(
            value=7.4, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))

        self.assertTrue(grp.in_bounds(
            value=7.4, gender=FEMALE, dob=report_datetime.date(),
            report_datetime=report_datetime,
            units='mg/dL'))

    def test_grading(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = utc.localize(datetime(2017, 12, 7))
        grp = ValueReferenceGroup(name='labtest')

        g2 = GradeReference(
            name='labtest',
            grade=2,
            lower=10,
            upper=20,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)
        self.assertTrue(repr(g2))

        g3 = GradeReference(
            name='labtest',
            grade=3,
            lower=20,
            lower_inclusive=True,
            upper=30,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)

        g4 = GradeReference(
            name='labtest',
            grade=4,
            lower=30,
            lower_inclusive=True,
            upper=40,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)

        grp.add_grading(g2)
        grp.add_grading(g3)
        grp.add_grading(g4)

        self.assertFalse(
            grp.in_bounds_for_grade(
                value=10, gender=MALE,
                dob=dob, report_datetime=report_datetime,
                units='mg/dL'))
        self.assertTrue(
            grp.in_bounds_for_grade(
                value=11, gender=MALE,
                dob=dob, report_datetime=report_datetime,
                units='mg/dL'))
        self.assertEqual(grp.success.get('grading')[0].grade, 2)

        self.assertTrue(
            grp.in_bounds_for_grade(
                value=20, gender=MALE,
                dob=dob, report_datetime=report_datetime,
                units='mg/dL'))
        self.assertEqual(grp.success.get('grading')[0].grade, 3)
        self.assertTrue(
            grp.in_bounds_for_grade(
                value=21, gender=MALE,
                dob=dob, report_datetime=report_datetime,
                units='mg/dL'))
        self.assertEqual(grp.success.get('grading')[0].grade, 3)

        self.assertTrue(
            grp.in_bounds_for_grade(
                value=30, gender=MALE,
                dob=dob, report_datetime=report_datetime,
                units='mg/dL'))
        self.assertEqual(grp.success.get('grading')[0].grade, 4)
        self.assertTrue(
            grp.in_bounds_for_grade(
                value=31, gender=MALE,
                dob=dob, report_datetime=report_datetime,
                units='mg/dL'))
        self.assertEqual(grp.success.get('grading')[0].grade, 4)
