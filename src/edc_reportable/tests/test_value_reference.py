from datetime import datetime
from dateutil.relativedelta import relativedelta
from edc_base.utils import get_utcnow, age
from edc_constants.constants import MALE, FEMALE
from pytz import utc
from unittest import TestCase

from ..age_evaluator import AgeEvaluator
from ..evaluator import Evaluator, ValueBoundryError, InvalidUpperBound
from ..evaluator import InvalidCombination, InvalidLowerBound, InvalidUnits
from ..grade_reference import GradeReference
from ..normal_reference import NormalReference
from ..reference_collection import ReferenceCollection, AlreadyRegistered
from ..value_reference_group import InvalidValueReference, NotEvaluated
from ..value_reference_group import ValueReferenceGroup, ValueReferenceAlreadyAdded


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
        self.assertEqual(ref.description(), 'value<100.0 in mg/dL')
        self.assertRaises(
            InvalidLowerBound, Evaluator, lower='ERIK', upper=100, units='mg/dL')
        self.assertRaises(
            InvalidUpperBound, Evaluator, lower=10, upper='ERIK', units='mg/dL')
        ref = Evaluator(lower=10, upper=None, units='mg/dL')
        self.assertEqual(ref.description(), '10.0<value in mg/dL')

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

    def test_value_reference_group(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = utc.localize(datetime(2017, 12, 7))
        grp = ValueReferenceGroup(name='labtest')
        self.assertTrue(repr(grp))

        ref = NormalReference(
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
            grp.add_normal, ref)

        ref = NormalReference(
            name='labtest',
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)
        grp.add_normal(ref)
        self.assertFalse(grp.get_normal(
            value=9,
            units='mg/dL',
            gender=MALE,
            dob=dob))
        self.assertFalse(grp.get_normal(
            value=10,
            units='mg/dL',
            gender=MALE,
            dob=dob))
        self.assertTrue(grp.get_normal(
            value=11,
            units='mg/dL',
            gender=MALE,
            dob=dob))
        self.assertRaises(
            ValueReferenceAlreadyAdded,
            grp.add_normal, ref)

        grp = ValueReferenceGroup(name='labtest')
        ref_male = NormalReference(
            name='labtest',
            lower=10,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=MALE)
        ref_female1 = NormalReference(
            name='labtest',
            lower=1.7,
            upper=3.5,
            upper_inclusive=True,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=FEMALE)
        ref_female2 = NormalReference(
            name='labtest',
            lower=7.3,
            upper=None,
            units='mg/dL',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=FEMALE)
        grp.add_normal(ref_male)
        grp.add_normal(ref_female1)
        grp.add_normal(ref_female2)

        self.assertFalse(grp.get_normal(
            value=9, gender=MALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertFalse(grp.get_normal(
            value=10, gender=MALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.get_normal(
            value=11, gender=MALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))

        self.assertFalse(grp.get_normal(
            value=1, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertFalse(grp.get_normal(
            value=1.7, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.get_normal(
            value=1.8, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.get_normal(
            value=3.4, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.get_normal(
            value=3.5, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertFalse(grp.get_normal(
            value=3.6, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))

        self.assertFalse(grp.get_normal(
            value=7.3, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))
        self.assertTrue(grp.get_normal(
            value=7.4, gender=FEMALE, dob=dob,
            report_datetime=report_datetime,
            units='mg/dL'))

        self.assertRaises(
            NotEvaluated,
            grp.get_normal,
            value=7.4, gender=FEMALE, dob=report_datetime.date(),
            report_datetime=report_datetime,
            units='mg/dL')

        self.assertRaises(
            NotEvaluated,
            grp.get_normal,
            value=7.4, gender=FEMALE, dob=report_datetime.date(),
            report_datetime=report_datetime,
            units='mmol/L')

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

        grade = grp.get_grade(
            value=10, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertIsNone(grade)
        grade = grp.get_grade(
            value=11, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertEqual(grade.grade, 2)

        grade = grp.get_grade(
            value=20, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertEqual(grade.grade, 3)
        grade = grp.get_grade(
            value=21, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertEqual(grade.grade, 3)

        grade = grp.get_grade(
            value=30, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertEqual(grade.grade, 4)
        grade = grp.get_grade(
            value=31, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertEqual(grade.grade, 4)

        self.assertRaises(
            NotEvaluated,
            grp.get_grade,
            value=31, gender=MALE,
            dob=report_datetime.date(), report_datetime=report_datetime,
            units='mg/dL')

        self.assertRaises(
            NotEvaluated,
            grp.get_grade,
            value=31, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mmol/L')

        self.assertRaises(
            NotEvaluated,
            grp.get_grade,
            value=31, gender=FEMALE,
            dob=dob, report_datetime=report_datetime,
            units='mmol/L')

        grade = grp.get_grade(
            value=1, gender=MALE,
            dob=dob, report_datetime=report_datetime,
            units='mg/dL')
        self.assertIsNone(grade)

    def test_collection(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = utc.localize(datetime(2017, 12, 7))
        reference = ReferenceCollection()
        neutrophils = ValueReferenceGroup(name='neutrophils')
        ln = NormalReference(
            name='neutrophils',
            lower=2.5,
            upper=7.5,
            units='10e9/L',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=[MALE, FEMALE])

        g3 = GradeReference(
            name='neutrophils',
            grade=3,
            lower=0.4,
            lower_inclusive=True,
            upper=0.59,
            upper_inclusive=True,
            units='10e9/L',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=[MALE, FEMALE])

        g4 = GradeReference(
            name='neutrophils',
            grade=4,
            lower=0,
            upper=0.4,
            units='10e9/L',
            age_lower=18,
            age_upper=99,
            age_units='years',
            gender=[MALE, FEMALE])

        neutrophils.add_normal(ln)
        neutrophils.add_grading(g3)
        neutrophils.add_grading(g4)

        reference.register(neutrophils)
        self.assertRaises(
            AlreadyRegistered,
            reference.register, neutrophils)
        self.assertTrue(reference.get(
            'neutrophils').get_normal(
                value=3.5, units='10e9/L',
                gender=MALE, dob=dob, report_datetime=report_datetime))

        neutrophils = reference.get('neutrophils')
        self.assertTrue(
            neutrophils.get_normal(
                value=3.5, units='10e9/L',
                gender=MALE, dob=dob, report_datetime=report_datetime))
        grade = neutrophils.get_grade(
            value=3.5, units='10e9/L',
            gender=MALE, dob=dob, report_datetime=report_datetime)
        self.assertIsNone(grade)

        grade = neutrophils.get_grade(
            value=.43, units='10e9/L',
            gender=MALE, dob=dob, report_datetime=report_datetime)
        self.assertEqual(grade.grade, 3)

        grade = neutrophils.get_grade(
            value=.3, units='10e9/L',
            gender=MALE, dob=dob, report_datetime=report_datetime)
        self.assertEqual(grade.grade, 4)
