from copy import copy
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_constants.constants import FEMALE, MALE
from edc_utils import get_utcnow

from edc_reportable import (
    IU_LITER,
    BoundariesOverlap,
    GradeError,
    GradeReference,
    NormalReference,
    NotEvaluated,
    ValueReferenceGroup,
    adult_age_options,
)
from edc_reportable.constants import HIGH_VALUE


class TestGrading(TestCase):
    def test_grading(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = datetime(2017, 12, 7).astimezone(ZoneInfo("UTC"))
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

    def test_grading_with_limits_normal(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = datetime(2017, 12, 7).astimezone(ZoneInfo("UTC"))
        grp = ValueReferenceGroup(name="amylase")
        normal_reference = NormalReference(
            name="amylase",
            gender=[MALE, FEMALE],
            units=IU_LITER,
            lower=25.0,
            upper=125.0,
            lower_inclusive=True,
            upper_inclusive=True,
            **adult_age_options,
        )
        opts = dict(
            name="amylase",
            grade=1,
            lower="1.1*ULN",
            upper="1.5*ULN",
            lower_inclusive=True,
            upper_inclusive=False,
            units=IU_LITER,
            gender=MALE,
            **adult_age_options,
        )
        g1 = GradeReference(normal_references={MALE: [normal_reference]}, **opts)

        new_opts = copy(opts)
        new_opts.update(grade=2, lower="1.5*ULN", upper="3.0*ULN")
        g2 = GradeReference(normal_references={MALE: [normal_reference]}, **new_opts)

        new_opts = copy(opts)
        new_opts.update(grade=3, lower="3.0*ULN", upper="5.0*ULN")
        g3 = GradeReference(normal_references={MALE: [normal_reference]}, **new_opts)

        new_opts = copy(opts)
        new_opts.update(grade=4, lower="5.0*ULN", upper=f"{HIGH_VALUE}*ULN")
        g4 = GradeReference(normal_references={MALE: [normal_reference]}, **new_opts)

        grp.add_grading(g1)
        grp.add_grading(g2)
        grp.add_grading(g3)
        grp.add_grading(g4)

        grade = grp.get_grade(
            value=130,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertIsNone(grade)

        grade = grp.get_grade(
            value=137.5,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertEqual(grade.grade, 1)

        grade = grp.get_grade(
            value=187.4,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertEqual(grade.grade, 1)

        grade = grp.get_grade(
            value=187.5,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertEqual(grade.grade, 2)

        grade = grp.get_grade(
            value=212,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertEqual(grade.grade, 2)

        grade = grp.get_grade(
            value=600,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertEqual(grade.grade, 3)

        grade = grp.get_grade(
            value=780,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
        )
        self.assertEqual(grade.grade, 4)

    # TODO:
    def test_grading_with_limits_normal_gender(self):
        pass
