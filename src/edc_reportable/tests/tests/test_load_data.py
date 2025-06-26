from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.test import TestCase
from edc_constants.constants import FEMALE, MALE
from edc_utils import get_utcnow

from edc_reportable import (
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    ConversionNotHandled,
)
from edc_reportable.evaluator import ValueBoundryError
from edc_reportable.models import GradingData, NormalData
from edc_reportable.utils import (
    get_normal_data_or_raise,
    in_normal_bounds_or_raise,
    load_reference_ranges,
)
from edc_reportable.utils.get_normal_data_or_raise import (
    create_obj_for_new_units_or_raise,
)
from reportable_app.reportables import grading_data, normal_data


class TestLoadData(TestCase):

    def test_load_data(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        self.assertEqual(NormalData.objects.all().count(), 24)
        self.assertEqual(GradingData.objects.all().count(), 60)

    def test_loaded_grades(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = GradingData.objects.values("grade").annotate(count=Count("grade"))
        self.assertEqual(qs.filter(grade=1)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=2)[0].get("count"), 4)
        self.assertEqual(qs.filter(grade=3)[0].get("count"), 26)
        self.assertEqual(qs.filter(grade=4)[0].get("count"), 26)

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

    def test_description(self):
        load_reference_ranges(
            "my_reportables", grading_data=grading_data, normal_data=normal_data
        )
        qs = GradingData.objects.filter(label="tbil").order_by("units", "grade")
        self.assertEqual(
            qs.first().description, "tbil: 1.1*ULN<=x<1.6*ULN mg/dL GRADE1 M 18<=AGE"
        )
        self.assertEqual(qs.last().description, "tbil: 5.0*ULN<=x mmol/L GRADE4 M 18<=AGE")

    def test_bounds_for_existing_units(self):

        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)

        for gender in [MALE, FEMALE]:
            self.assertRaises(
                ValueBoundryError,
                in_normal_bounds_or_raise,
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
                in_normal_bounds_or_raise(
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
                in_normal_bounds_or_raise(
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
                in_normal_bounds_or_raise,
                reference_range_collection,
                "tbil",
                21.0,
                MICROMOLES_PER_LITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )

    def test_normal_data_bounds_for_non_existing_units(self):

        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)

        for gender in [MALE, FEMALE]:
            self.assertRaises(
                ValueBoundryError,
                in_normal_bounds_or_raise,
                reference_range_collection,
                "tbil",
                0.05,
                MILLIGRAMS_PER_DECILITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
            in_normal_bounds_or_raise(
                reference_range_collection,
                "tbil",
                1.1,
                MILLIGRAMS_PER_DECILITER,
                gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )

            self.assertTrue(
                in_normal_bounds_or_raise(
                    reference_range_collection,
                    "tbil",
                    1.0,
                    MILLIGRAMS_PER_DECILITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                    age_units="years",
                )
            )
            self.assertTrue(
                in_normal_bounds_or_raise(
                    reference_range_collection,
                    "tbil",
                    1.225,
                    MILLIGRAMS_PER_DECILITER,
                    gender,
                    dob=dob,
                    report_datetime=report_datetime,
                    age_units="years",
                )
            )
            self.assertRaises(
                ValueBoundryError,
                in_normal_bounds_or_raise,
                reference_range_collection,
                "tbil",
                1.228,
                MILLIGRAMS_PER_DECILITER,
                gender=gender,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )

    def test_auto_create_new_normal_data(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        self.assertTrue(
            NormalData.objects.filter(label="tbil", units=MILLIGRAMS_PER_DECILITER).exists()
        )

        NormalData.objects.filter(label="tbil", units=MILLIGRAMS_PER_DECILITER).delete()

        opts = dict(
            reference_range_collection=reference_range_collection,
            label="tbil",
            gender=FEMALE,
            units=MILLIGRAMS_PER_DECILITER,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
        )

        create_obj_for_new_units_or_raise(**opts)

        self.assertTrue(
            NormalData.objects.filter(label="tbil", units=MILLIGRAMS_PER_DECILITER).exists()
        )

    def test_auto_create_new_normal_data2(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )

        self.assertTrue(
            NormalData.objects.filter(label="tbil", units=MICROMOLES_PER_LITER).exists()
        )

        NormalData.objects.filter(label="tbil", units=MICROMOLES_PER_LITER).delete()

        opts = dict(
            reference_range_collection=reference_range_collection,
            label="tbil",
            gender=FEMALE,
            units=MICROMOLES_PER_LITER,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
        )
        create_obj_for_new_units_or_raise(**opts)

        self.assertTrue(
            NormalData.objects.filter(label="tbil", units=MICROMOLES_PER_LITER).exists()
        )

        get_normal_data_or_raise(
            reference_range_collection=reference_range_collection,
            label="tbil",
            gender=FEMALE,
            units=MICROMOLES_PER_LITER,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
            create_missing_normal=False,
        )

    def test_normal_data_raises_if_no_mw(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )
        self.assertRaises(
            ConversionNotHandled,
            get_normal_data_or_raise,
            reference_range_collection=reference_range_collection,
            label="magnesium",
            units=MILLIGRAMS_PER_DECILITER,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
            create_missing_normal=True,
        )

    def test_normal_data_creates_for_missing_units(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )
        NormalData.objects.filter(label="tbil", units=MILLIGRAMS_PER_DECILITER).delete()

        starting_count = NormalData.objects.filter(label="tbil").count()

        obj = get_normal_data_or_raise(
            reference_range_collection=reference_range_collection,
            label="tbil",
            units=MILLIGRAMS_PER_DECILITER,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
            create_missing_normal=True,
        )
        self.assertEqual(NormalData.objects.filter(label="tbil").count(), starting_count + 1)
        self.assertEqual(obj.description, "tbil: 0.2923<=x<1.2277 mg/dL M 18<=AGE")

        # do again to ensure does not create duplicates
        get_normal_data_or_raise(
            reference_range_collection=reference_range_collection,
            label="tbil",
            units=MILLIGRAMS_PER_DECILITER,
            gender=MALE,
            dob=dob,
            report_datetime=report_datetime,
            age_units="years",
            create_missing_normal=True,
        )
        self.assertEqual(NormalData.objects.filter(label="tbil").count(), starting_count + 1)

    def test_normal_data_creates_for_missing_units_and_evaluates(self):
        report_datetime = get_utcnow()
        dob = report_datetime - relativedelta(years=25)
        reference_range_collection = load_reference_ranges(
            "test_ranges", normal_data=normal_data, grading_data=grading_data
        )
        # these units are missing
        self.assertTrue(
            in_normal_bounds_or_raise(
                reference_range_collection,
                "tbil",
                0.3000,
                MILLIGRAMS_PER_DECILITER,
                MALE,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
                create_missing_normal=True,
            )
        )
        self.assertTrue(
            in_normal_bounds_or_raise(
                reference_range_collection,
                "tbil",
                10.2622,
                MICROMOLES_PER_LITER,
                MALE,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
                create_missing_normal=True,
            )
        )
        # these units are not missing
        self.assertTrue(
            in_normal_bounds_or_raise(
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
            in_normal_bounds_or_raise(
                reference_range_collection,
                "tbil",
                1.022,
                MILLIGRAMS_PER_DECILITER,
                MALE,
                dob=dob,
                report_datetime=report_datetime,
                age_units="years",
            )
        )
