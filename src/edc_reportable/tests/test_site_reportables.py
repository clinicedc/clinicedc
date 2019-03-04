from dateutil.relativedelta import relativedelta
from django.test.testcases import TestCase
from edc_utils import get_utcnow
from edc_constants.constants import MALE
from tempfile import mkdtemp

from ..site_reportables import site_reportables
from .reportables import normal_data, grading_data


class TestSiteReportables(TestCase):
    def setUp(self):
        site_reportables._registry = {}

        site_reportables.register(
            name="my_project", normal_data=normal_data, grading_data=grading_data
        )

    def test_to_csv(self):
        path = mkdtemp()
        site_reportables.to_csv(collection_name="my_project", path=path)

    def test_(self):
        reportables = site_reportables.get("my_project")
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
