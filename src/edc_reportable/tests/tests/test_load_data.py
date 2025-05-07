from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.test import TestCase, tag
from edc_constants.constants import FEMALE, MALE
from edc_utils import get_utcnow

from edc_reportable import MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER
from edc_reportable.evaluator import ValueBoundryError
from edc_reportable.models import GradingData, NormalData, in_bounds_or_raise
from edc_reportable.models.load_data import load_reference_ranges
from reportable_app.reportables import grading_data, normal_data


class TestLoadData(TestCase):
    @tag("5")
    def test_load_data(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 20)
        self.assertEqual(GradingData.objects.all().count(), 60)

    @tag("5")
    def test_loaded_grades(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = GradingData.objects.values("grade").annotate(count=Count("grade"))
        self.assertEqual(qs.filter(grade=1)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=2)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=3)[0].get("count"), 26)
        self.assertEqual(qs.filter(grade=4)[0].get("count"), 26)

    @tag("5")
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

    @tag("5")
    def test_loaded_twice_ok(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 20)
        self.assertEqual(GradingData.objects.all().count(), 60)
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 20)
        self.assertEqual(GradingData.objects.all().count(), 60)

    @tag("8")
    def test_description(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = GradingData.objects.filter(label="tbil").order_by("units", "grade")
        self.assertEqual(qs.first().description, "1.1<=x<1.6 M,F 18<=AGE")
        self.assertEqual(qs.last().description, "5.0<=x M,F 18<=AGE")

    @tag("12")
    def test_bounds(self):

        load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)

        for gender in [MALE, FEMALE]:
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                "tbil",
                4.9,
                MICROMOLES_PER_LITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
            )
            self.assertTrue(
                in_bounds_or_raise(
                    "tbil",
                    7.1,
                    MICROMOLES_PER_LITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                )
            )
            self.assertTrue(
                in_bounds_or_raise(
                    "tbil",
                    20.9,
                    MICROMOLES_PER_LITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                )
            )
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                "tbil",
                21.0,
                MICROMOLES_PER_LITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
            )
        for gender in [MALE, FEMALE]:
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                "tbil",
                0.05,
                MILLIGRAMS_PER_DECILITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
            )
            self.assertTrue(
                in_bounds_or_raise(
                    "tbil",
                    0.06,
                    MILLIGRAMS_PER_DECILITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                )
            )
            self.assertTrue(
                in_bounds_or_raise(
                    "tbil",
                    0.23,
                    MILLIGRAMS_PER_DECILITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                )
            )
            self.assertRaises(
                ValueBoundryError,
                in_bounds_or_raise,
                "tbil",
                0.24,
                MILLIGRAMS_PER_DECILITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
            )
