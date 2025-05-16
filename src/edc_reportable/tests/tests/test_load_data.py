from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.test import TestCase, tag
from edc_constants.constants import FEMALE, MALE
from edc_utils import get_utcnow

from edc_reportable import MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER
from edc_reportable.evaluator import ValueBoundryError
from edc_reportable.models import (
    GradingData,
    NormalData,
    get_normal_data_or_raise,
    in_bounds_or_raise,
)
from edc_reportable.models.load_data import load_reference_ranges
from reportable_app.reportables import grading_data, normal_data


class TestLoadData(TestCase):
    @tag("1")
    def test_load_data(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 24)
        self.assertEqual(GradingData.objects.all().count(), 60)

    @tag("1")
    def test_loaded_grades(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = GradingData.objects.values("grade").annotate(count=Count("grade"))
        self.assertEqual(qs.filter(grade=1)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=2)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=3)[0].get("count"), 26)
        self.assertEqual(qs.filter(grade=4)[0].get("count"), 26)

    @tag("1")
    def test_loaded_grades_tbil(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = (
            GradingData.objects.values("grade")
            .filter(label="tbil")
            .annotate(count=Count("grade"))
        )
        self.assertEqual(qs.filter(grade=1)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=2)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=3)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=4)[0].get("count"), 4)

    @tag("1")
    def test_loaded_twice_ok(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 24)
        self.assertEqual(GradingData.objects.all().count(), 60)
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 24)
        self.assertEqual(GradingData.objects.all().count(), 60)

    @tag("1")
    def test_description(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = GradingData.objects.filter(label="tbil").order_by("units", "grade")
        self.assertEqual(qs.first().description, "tbil: 1.1*ULN<=x<1.6*ULN mg/dL M 18<=AGE")
        self.assertEqual(qs.last().description, "tbil: 5.0*ULN<=x mmol/L M 18<=AGE")

    @tag("1")
    def test_bounds_for_existing_units(self):

        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)

        for gender in [MALE, FEMALE]:
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                reference_range_collection,
                "tbil",
                4.9,
                MICROMOLES_PER_LITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
            self.assertTrue(
                in_bounds_or_raise(
                    reference_range_collection,
                    "tbil",
                    7.1,
                    MICROMOLES_PER_LITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                    age_units="years",
                )
            )
            self.assertTrue(
                in_bounds_or_raise(
                    reference_range_collection,
                    "tbil",
                    20.9,
                    MICROMOLES_PER_LITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                    age_units="years",
                )
            )
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                reference_range_collection,
                "tbil",
                21.0,
                MICROMOLES_PER_LITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )

    @tag("1")
    def test_normal_data_bounds_for_non_existing_units(self):

        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)

        for gender in [MALE, FEMALE]:
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                reference_range_collection,
                "tbil",
                0.05,
                MILLIGRAMS_PER_DECILITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
            in_bounds_or_raise(
                reference_range_collection,
                "tbil",
                0.06,
                MILLIGRAMS_PER_DECILITER,
                gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )

            self.assertTrue(
                in_bounds_or_raise(
                    reference_range_collection,
                    "tbil",
                    0.06,
                    MILLIGRAMS_PER_DECILITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                    age_units="years",
                )
            )
            self.assertTrue(
                in_bounds_or_raise(
                    reference_range_collection,
                    "tbil",
                    0.23,
                    MILLIGRAMS_PER_DECILITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                    age_units="years",
                )
            )
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                reference_range_collection,
                "tbil",
                0.24,
                MILLIGRAMS_PER_DECILITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )

    @tag("1")
    def test_normal_data_creates_for_missing_units(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )
        starting_count = NormalData.objects.filter(label="magnesium").count()
        obj = get_normal_data_or_raise(
            reference_range_collection=reference_range_collection,
            label="magnesium",
            units=MILLIGRAMS_PER_DECILITER,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
        )
        self.assertEqual(
            NormalData.objects.filter(label="magnesium").count(), starting_count + 1
        )
        self.assertEqual(obj.description, "magnesium: 13.51<=x<=21.62 mg/dL M 18<=AGE")

        # do again to ensure does not create duplicates
        get_normal_data_or_raise(
            reference_range_collection=reference_range_collection,
            label="magnesium",
            units=MILLIGRAMS_PER_DECILITER,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
        )
        self.assertEqual(
            NormalData.objects.filter(label="magnesium").count(), starting_count + 1
        )

    @tag("1")
    def test_normal_data_creates_for_missing_units_and_evaluates(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )
        # these units are missing
        self.assertTrue(
            in_bounds_or_raise(
                reference_range_collection,
                "tbil",
                0.06,
                MILLIGRAMS_PER_DECILITER,
                MALE,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
        )
        # these units are not missing
        self.assertTrue(
            in_bounds_or_raise(
                reference_range_collection,
                "tbil",
                7.1,
                MICROMOLES_PER_LITER,
                MALE,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
        )
        # these units were missing
        self.assertTrue(
            in_bounds_or_raise(
                reference_range_collection,
                "tbil",
                0.06,
                MILLIGRAMS_PER_DECILITER,
                MALE,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
        )
