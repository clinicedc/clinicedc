import os
from tempfile import mkdtemp

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_constants.constants import MALE
from edc_utils import get_utcnow

from edc_reportable import IU_LITER, site_reportables
from edc_reportable.grading_data.daids_july_2017 import chemistries
from edc_reportable.normal_data.africa import normal_data as africa_normal_data
from reportable_app.reportables import grading_data, normal_data


class TestSiteReportables(TestCase):
    def setUp(self):
        site_reportables._registry = {}

        site_reportables.register(
            name="my_reference_list", normal_data=normal_data, grading_data=grading_data
        )

    def test_to_csv(self):
        path = mkdtemp()
        filename1, filename2 = site_reportables.to_csv(
            collection_name="my_reference_list", path=path
        )
        with open(os.path.join(path, filename1)) as f:
            header = str(f.readline()).strip()
            self.assertEqual(
                header,
                (
                    "name,description,units,gender,lower,upper,lower_inclusive,"
                    "upper_inclusive,fasting,age_lower,age_upper,"
                    "age_units,age_lower_inclusive"
                ),
            )

    def test_haemoglobin(self):
        reportables = site_reportables.get("my_reference_list")
        haemoglobin = reportables.get("haemoglobin")
        normal = haemoglobin.get_normal(
            value=15.0,
            units="g/dL",
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertIsNotNone(normal)
        self.assertIn("13.5<=15.0<=17.5", normal.description)

        grade = haemoglobin.get_grade(
            value=8,
            units="g/dL",
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertIn("7.0<=8.0<9.0", grade.description)

        grade = haemoglobin.get_grade(
            value=15,
            units="g/dL",
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertIsNone(grade)


class TestSiteReportablesDiads2017(TestCase):
    def setUp(self):
        site_reportables._registry = {}
        grading_data.update(**chemistries)
        site_reportables.register(
            name="my_reference_list", normal_data=africa_normal_data, grading_data=grading_data
        )

    def test_daids_2017(self):
        reportables = site_reportables.get("my_reference_list")
        amylase = reportables.get("amylase")
        normal = amylase.get_normal(
            value=50,
            units=IU_LITER,
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.assertIsNotNone(normal)
        self.assertIn("25.0<=50.0<=125.0", normal.description)
