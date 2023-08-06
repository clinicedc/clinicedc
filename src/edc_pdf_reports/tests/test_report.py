from uuid import uuid4

from django.test import TestCase

from .my_report import MyReport


class TestReport(TestCase):
    def test_report(self):
        report = MyReport(filename=f"{uuid4()}.pdf")
        response = report.render_to_response()
        self.assertEqual(response.status_code, 200)
        self.assertIn("ReportLab Generated PDF document", str(response.content))
