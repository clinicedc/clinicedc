import os

from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_constants.constants import MALE
from edc_reportable import site_reportables
from edc_utils import get_utcnow
from tempfile import mkdtemp
from reportable_app.reportables import normal_data, grading_data


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
                    "name,description,units,gender,lower,lower_inclusive,"
                    "upper,upper_inclusive,fasting,age_lower,age_upper,"
                    "age_units,age_lower_inclusive"
                ),
            )

    def test_(self):
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
