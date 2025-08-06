from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_constants.constants import FEMALE, MALE
from edc_utils import get_utcnow

from edc_reportable import Formula
from edc_reportable.adult_age_options import adult_age_options
from edc_reportable.constants import HIGH_VALUE
from edc_reportable.exceptions import BoundariesOverlap, NotEvaluated
from edc_reportable.models import ReferenceRangeCollection
from edc_reportable.units import (
    IU_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
)
from edc_reportable.utils import (
    get_grade_for_value,
    update_grading_data,
    update_normal_data,
)


class TestGrading(TestCase):

    def setUp(self):
        self.reference_range_collection = ReferenceRangeCollection.objects.create(
            name="my_references"
        )
        self.age_opts = dict(
            age_lower=18, age_upper=None, age_units="years", age_lower_inclusive=True
        )

    def test_grading(self):
        update_normal_data(
            self.reference_range_collection,
            normal_data={
                "labtest": [
                    Formula(
                        "3.0<=x<7.0",
                        units=MILLIGRAMS_PER_DECILITER,
                        gender=[MALE, FEMALE],
                        **self.age_opts,
                    ),
                ],
            },
        )
        report_datetime = datetime(2017, 12, 7).astimezone(ZoneInfo("UTC"))
        dob = report_datetime - relativedelta(years=25)

        data = {
            "labtest": [
                Formula(
                    "10.0<=x<20.0",
                    grade=2,
                    units=MILLIGRAMS_PER_DECILITER,
                    gender=[MALE],
                    **self.age_opts,
                ),
                Formula(
                    "20.0<=x<30.0",
                    grade=3,
                    units=MILLIGRAMS_PER_DECILITER,
                    gender=[MALE],
                    **self.age_opts,
                ),
                Formula(
                    "30.0<=x<40.0",
                    grade=4,
                    units=MILLIGRAMS_PER_DECILITER,
                    gender=[MALE],
                    **self.age_opts,
                ),
            ]
        }
        update_grading_data(self.reference_range_collection, grading_data=data)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=9.9,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertIsNone(grading_data)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=11,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertEqual(grading_data.grade, 2)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=20,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertEqual(grading_data.grade, 3)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=21,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertEqual(grading_data.grade, 3)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=30,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertEqual(grading_data.grade, 4)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=31,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertEqual(grading_data.grade, 4)

        self.assertRaises(
            NotEvaluated,
            get_grade_for_value,
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=31,
            gender=MALE,
            dob=report_datetime.date(),
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )

        self.assertRaises(
            NotEvaluated,
            get_grade_for_value,
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=31,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIMOLES_PER_LITER,
            age_units="years",
        )

        self.assertRaises(
            NotEvaluated,
            get_grade_for_value,
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=31,
            gender=FEMALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIMOLES_PER_LITER,
            age_units="years",
        )

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="labtest",
            value=1,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=MILLIGRAMS_PER_DECILITER,
            age_units="years",
        )
        self.assertIsNone(grading_data)

    def test_grading_boundaries_overlap(self):
        update_normal_data(
            self.reference_range_collection,
            normal_data={
                "labtest": [
                    Formula(
                        "3.0<=x<7.0",
                        units=MILLIGRAMS_PER_DECILITER,
                        gender=[MALE, FEMALE],
                        **self.age_opts,
                    ),
                ],
            },
        )

        data = {
            "labtest": [
                Formula(
                    "10.0<=x<20.0",
                    grade=2,
                    units=MILLIGRAMS_PER_DECILITER,
                    gender=[MALE],
                    **self.age_opts,
                ),
                Formula(
                    "20.0<=x<30.0",
                    grade=3,
                    units=MILLIGRAMS_PER_DECILITER,
                    gender=[MALE],
                    **self.age_opts,
                ),
                Formula(
                    "30.0<=x<40.0",
                    grade=4,
                    units=MILLIGRAMS_PER_DECILITER,
                    gender=[MALE],
                    **self.age_opts,
                ),
            ]
        }
        update_grading_data(self.reference_range_collection, grading_data=data)

        overlapping_formula = Formula(
            "15.0<=x<20.0",
            grade=1,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE],
            **self.age_opts,
        )

        data["labtest"] = [overlapping_formula]
        self.assertRaises(
            BoundariesOverlap,
            update_grading_data,
            self.reference_range_collection,
            grading_data=data,
            keep_existing=True,
        )

    def test_grading_with_limits_normal(self):
        dob = get_utcnow() - relativedelta(years=25)
        report_datetime = get_utcnow()

        update_normal_data(
            self.reference_range_collection,
            normal_data={
                "amylase": [
                    Formula(
                        "25<=x<=125", units=IU_LITER, gender=[MALE, FEMALE], **self.age_opts
                    )
                ]
            },
        )
        update_grading_data(
            self.reference_range_collection,
            grading_data={
                "amylase": [
                    Formula(
                        "1.1*ULN<=x<1.5*ULN",
                        grade=1,
                        units=IU_LITER,
                        gender=[MALE, FEMALE],
                        **adult_age_options,
                    ),
                    Formula(
                        "1.5*ULN<=x<3.0*ULN",
                        grade=2,
                        units=IU_LITER,
                        gender=[MALE, FEMALE],
                        **adult_age_options,
                    ),
                    Formula(
                        "3.0*ULN<=x<5.0*ULN",
                        grade=3,
                        units=IU_LITER,
                        gender=[MALE, FEMALE],
                        **adult_age_options,
                    ),
                    Formula(
                        f"5.0*ULN<=x<{HIGH_VALUE}*ULN",
                        grade=4,
                        units=IU_LITER,
                        gender=[MALE, FEMALE],
                        **adult_age_options,
                    ),
                ],
            },
        )
        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=130,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertIsNone(grading_data)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=137.5,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertEqual(grading_data.grade, 1)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=187.4,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertEqual(grading_data.grade, 1)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=187.5,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertEqual(grading_data.grade, 2)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=212,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertEqual(grading_data.grade, 2)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=600,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertEqual(grading_data.grade, 3)

        grading_data, _ = get_grade_for_value(
            reference_range_collection=self.reference_range_collection,
            label="amylase",
            value=780,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            units=IU_LITER,
            age_units=self.age_opts["age_units"],
        )
        self.assertEqual(grading_data.grade, 4)

    # TODO:
    def test_grading_with_limits_normal_gender(self):
        pass
