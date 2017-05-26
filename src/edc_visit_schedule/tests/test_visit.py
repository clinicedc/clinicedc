from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag

from ..visit import Crf, WindowPeriod, FormsCollection, FormsCollectionError
from ..visit import Visit, VisitCodeError, VisitDateError


@tag('visit')
class TestVisit(TestCase):

    def test_visit_title(self):
        visit = Visit(code='1000',
                      rbase=relativedelta(days=0),
                      rlower=relativedelta(days=0),
                      rupper=relativedelta(days=6))
        self.assertEqual(visit.title, 'Visit 1000')
        self.assertEqual(str(visit), 'Visit 1000')

    def test_visit_lower_upper_no_datetime(self):
        visit = Visit(code='1000',
                      rbase=relativedelta(days=0),
                      rlower=relativedelta(days=0),
                      rupper=relativedelta(days=6))
        try:
            visit.lower_date
        except VisitDateError:
            pass
        try:
            visit.upper_date
        except VisitDateError:
            pass

    def test_visit_lower_upper(self):
        visit = Visit(code='1000',
                      rbase=relativedelta(days=0),
                      rlower=relativedelta(days=0),
                      rupper=relativedelta(days=6))
        visit.base_date = datetime(2001, 12, 1)
        self.assertEqual(visit.lower_date, datetime(2001, 12, 1))
        self.assertEqual(visit.upper_date, datetime(2001, 12, 7))

    def test_window_period_days(self):
        wp = WindowPeriod(
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6))
        dt = datetime(2001, 12, 1)
        self.assertEqual(wp.window(dt)[0], dt)
        self.assertEqual(wp.window(dt).lower, dt)
        self.assertEqual(wp.window(dt)[1], datetime(2001, 12, 7))
        self.assertEqual(wp.window(dt).upper, datetime(2001, 12, 7))

    def test_window_period_weeks(self):
        wp = WindowPeriod(
            rlower=relativedelta(weeks=1),
            rupper=relativedelta(weeks=6))
        dt = datetime(2001, 12, 8)
        self.assertEqual(wp.window(dt).lower, datetime(2001, 12, 1))
        self.assertEqual(wp.window(dt).upper, datetime(2002, 1, 19))

    def test_good_codes(self):
        try:
            Visit(code='1000',
                  rbase=relativedelta(days=0),
                  rlower=relativedelta(days=0),
                  rupper=relativedelta(days=6))
        except (VisitCodeError) as e:
            self.fail(f'VisitError unexpectedly raised. Got {e}')
        try:
            Visit(code='1000',
                  rbase=relativedelta(days=0),
                  rlower=relativedelta(days=0),
                  rupper=relativedelta(days=6))
        except (VisitCodeError) as e:
            self.fail(f'VisitError unexpectedly raised. Got {e}')

    def test_no_code(self):
        self.assertRaises(
            VisitCodeError, Visit, code=None,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6))

    def test_bad_code_not_string(self):
        self.assertRaises(
            VisitCodeError, Visit, code=1,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6))

    def test_bad_code_format(self):
        self.assertRaises(
            VisitCodeError, Visit, code='Aa-1',
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6))

    def test_forms_collection_empty(self):
        items = []
        try:
            FormsCollection(*items)
        except FormsCollectionError as e:
            self.fail(f'FormsCollectionError unexpectedly raised. Got {e}')

    def test_forms_collection_none1(self):
        items = None
        try:
            FormsCollection(items)
        except FormsCollectionError as e:
            self.fail(f'FormsCollectionError unexpectedly raised. Got {e}')

    def test_forms_collection_order(self):
        items = []
        for i in range(0, 10):
            items.append(Crf(show_order=i, model='x.x'))
        try:
            FormsCollection(*items)
        except FormsCollectionError as e:
            self.fail(f'FormsCollectionError unexpectedly raised. Got {e}')
        items.append(0)
        self.assertRaises(FormsCollectionError, FormsCollection, *items)
