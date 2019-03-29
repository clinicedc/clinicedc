from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_utils import get_utcnow
from edc_visit_tracking.crf_date_validator import (
    CrfDateValidator,
    CrfReportDateAllowanceError,
    CrfReportDateIsFuture,
)


class TestVisitDateValidator(TestCase):
    def test_cls_ok(self):
        dt = get_utcnow()
        CrfDateValidator(report_datetime=dt, visit_report_datetime=dt)

    def test_raises_if_report_datetime_before_visit(self):
        dt = get_utcnow()
        self.assertRaises(
            CrfReportDateAllowanceError,
            CrfDateValidator,
            report_datetime=dt - relativedelta(days=1),
            visit_report_datetime=dt,
        )

    def test_raises_if_report_datetime_is_future(self):
        dt = get_utcnow()
        self.assertRaises(
            CrfReportDateIsFuture,
            CrfDateValidator,
            report_datetime=dt + relativedelta(years=10),
            visit_report_datetime=dt,
        )

    def test_report_datetime_ok(self):
        class MyCrfDateValidator(CrfDateValidator):
            report_datetime_allowance = 3

        visit_report_datetime = get_utcnow() - relativedelta(days=10)
        for days in range(0, 3):
            with self.subTest(days=days):
                try:
                    MyCrfDateValidator(
                        report_datetime=visit_report_datetime
                        + relativedelta(days=days),
                        visit_report_datetime=visit_report_datetime,
                    )
                except CrfReportDateAllowanceError as e:
                    self.fail(
                        f"VisitReportDateAllowanceError unexpectedly raised. Got {e}"
                    )

    def test_raises_if_report_datetime(self):
        class MyCrfDateValidator(CrfDateValidator):
            report_datetime_allowance = 3

        visit_report_datetime = get_utcnow() - relativedelta(days=10)
        self.assertRaises(
            CrfReportDateAllowanceError,
            MyCrfDateValidator,
            report_datetime=visit_report_datetime + relativedelta(days=4),
            visit_report_datetime=visit_report_datetime,
        )
