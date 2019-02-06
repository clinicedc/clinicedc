from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag

from ..visit import WindowPeriod
from ..visit import Visit, VisitCodeError, VisitDateError


class TestVisit(TestCase):
    def test_repr(self):
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertIsNotNone(visit.__repr__())

    def test_name(self):
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertEqual(visit.name, "1000")

    def test_visit_title(self):
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertEqual(visit.title, "Visit 1000")
        self.assertEqual(str(visit), "Visit 1000")

    def test_visit_datetime(self):
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        visit.timepoint_datetime = datetime(2001, 12, 1)
        self.assertEqual(visit.timepoint_datetime, datetime(2001, 12, 1))

    def test_visit_lower_upper_no_datetime(self):
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        try:
            visit.dates.lower
        except VisitDateError:
            pass
        try:
            visit.dates.upper
        except VisitDateError:
            pass

    def test_visit_lower_upper(self):
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        visit.timepoint_datetime = datetime(2001, 12, 1)
        self.assertEqual(visit.dates.lower, datetime(2001, 12, 1))
        self.assertEqual(visit.dates.upper, datetime(2001, 12, 7))

    def test_window_period_days(self):
        wp = WindowPeriod(rlower=relativedelta(days=0), rupper=relativedelta(days=6))
        dt = datetime(2001, 12, 1)
        self.assertEqual(wp.get_window(dt)[0], dt)
        self.assertEqual(wp.get_window(dt).lower, dt)
        self.assertEqual(wp.get_window(dt)[1], datetime(2001, 12, 7))
        self.assertEqual(wp.get_window(dt).upper, datetime(2001, 12, 7))

    def test_window_period_weeks(self):
        wp = WindowPeriod(rlower=relativedelta(weeks=1), rupper=relativedelta(weeks=6))
        dt = datetime(2001, 12, 8)
        self.assertEqual(wp.get_window(dt).lower, datetime(2001, 12, 1))
        self.assertEqual(wp.get_window(dt).upper, datetime(2002, 1, 19))

    def test_good_codes(self):
        try:
            Visit(
                code="1000",
                rbase=relativedelta(days=0),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
        except (VisitCodeError) as e:
            self.fail(f"VisitError unexpectedly raised. Got {e}")
        try:
            Visit(
                code="1000",
                rbase=relativedelta(days=0),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
        except (VisitCodeError) as e:
            self.fail(f"VisitError unexpectedly raised. Got {e}")

    def test_no_code(self):
        self.assertRaises(
            VisitCodeError,
            Visit,
            code=None,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )

    def test_bad_code_not_string(self):
        self.assertRaises(
            VisitCodeError,
            Visit,
            code=1,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )

    def test_bad_code_format(self):
        self.assertRaises(
            VisitCodeError,
            Visit,
            code="Aa-1",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
