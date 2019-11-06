from copy import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_constants.constants import MALE, FEMALE
from edc_reportable import (
    BoundariesOverlap,
    GradeError,
    GradeReference,
    NotEvaluated,
    ValueReferenceGroup,
)
from edc_utils import get_utcnow
from pytz import utc


class TestGrading(TestCase):
    def test_grading(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = utc.localize(datetime(2017, 12, 7))
        grp = ValueReferenceGroup(name="labtest")

        opts = dict(
            name="labtest",
            grade=2,
            lower=10,
            upper=20,
            units="mg/dL",
            age_lower=18,
            age_upper=99,
            age_units="years",
            gender=MALE,
        )

        g2 = GradeReference(**opts)
        self.assertTrue(repr(g2))

        new_opts = copy(opts)
        new_opts.update(grade="-1")
        self.assertRaises(GradeError, GradeReference, **new_opts)

        for grade in range(0, 6):
            new_opts = copy(opts)
            new_opts.update(grade=str(grade))
            try:
                GradeReference(**new_opts)
            except GradeError:
                self.fail("GradeError unexpectedly raised")

        new_opts = copy(opts)
        new_opts.update(grade=3, lower=20, lower_inclusive=True, upper=30)
        g3 = GradeReference(**new_opts)

        new_opts = copy(opts)
        new_opts.update(grade=4, lower=30, lower_inclusive=True, upper=40)
        g4 = GradeReference(**new_opts)

        grp.add_grading(g2)
        grp.add_grading(g3)
        grp.add_grading(g4)

        grade = grp.get_grade(
            value=10,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertIsNone(grade)
        grade = grp.get_grade(
            value=11,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertEqual(grade.grade, 2)

        grade = grp.get_grade(
            value=20,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertEqual(grade.grade, 3)
        grade = grp.get_grade(
            value=21,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertEqual(grade.grade, 3)

        grade = grp.get_grade(
            value=30,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertEqual(grade.grade, 4)
        grade = grp.get_grade(
            value=31,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertEqual(grade.grade, 4)

        self.assertRaises(
            NotEvaluated,
            grp.get_grade,
            value=31,
            gender=MALE,
            dob=report_datetime.date(),
            report_datetime=report_datetime,
            units="mg/dL",
        )

        self.assertRaises(
            NotEvaluated,
            grp.get_grade,
            value=31,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mmol/L",
        )

        self.assertRaises(
            NotEvaluated,
            grp.get_grade,
            value=31,
            gender=FEMALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mmol/L",
        )

        grade = grp.get_grade(
            value=1,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
        self.assertIsNone(grade)

        new_opts = copy(opts)
        new_opts.update(grade=1, lower=15, upper=20)

        # overlaps with G2
        g1 = GradeReference(**new_opts)
        grp.add_grading(g1)

        self.assertRaises(
            BoundariesOverlap,
            grp.get_grade,
            value=16,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units="mg/dL",
        )
