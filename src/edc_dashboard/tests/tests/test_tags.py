from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from django.test import TestCase
from edc_utils.date import get_utcnow

from edc_dashboard.templatetags.edc_dashboard_extras import (
    age_in_years,
    human,
    page_numbers,
    paginator_row,
)

from ..models import TestModel


class TestTags(TestCase):
    def test_(self):
        for i in range(0, 100):
            TestModel.objects.create(f1=f"object{i}")

        object_list = TestModel.objects.all()
        paginator = Paginator(object_list, 5)

        page = 1
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url="listboard_url",
        )
        context = paginator_row(context)
        self.assertIsNone(context.get("first_url"))
        self.assertIsNone(context.get("previous_url"))
        self.assertEqual(context.get("next_url"), "/subject_listboard/2/")
        self.assertEqual(context.get("last_url"), "/subject_listboard/20/")
        self.assertEqual(context.get("numbers")[0].number, 1)
        self.assertEqual(context.get("numbers")[-1:][0].number, 10)

        page = 2
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url="listboard_url",
        )
        context = paginator_row(context)
        self.assertEqual(context.get("first_url"), "/subject_listboard/1/")
        self.assertEqual(context.get("previous_url"), "/subject_listboard/1/")
        self.assertEqual(context.get("next_url"), "/subject_listboard/3/")
        self.assertEqual(context.get("last_url"), "/subject_listboard/20/")
        self.assertEqual(context.get("numbers")[0].number, 1)
        self.assertEqual(context.get("numbers")[-1:][0].number, 10)

        page = 3
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url="listboard_url",
        )
        context = paginator_row(context)
        self.assertEqual(context.get("first_url"), "/subject_listboard/1/")
        self.assertEqual(context.get("previous_url"), "/subject_listboard/2/")
        self.assertEqual(context.get("next_url"), "/subject_listboard/4/")
        self.assertEqual(context.get("last_url"), "/subject_listboard/20/")
        self.assertEqual(context.get("numbers")[0].number, 1)
        self.assertEqual(context.get("numbers")[-1:][0].number, 10)

        page = 20
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url="listboard_url",
        )
        context = paginator_row(context)
        self.assertEqual(context.get("first_url"), "/subject_listboard/1/")
        self.assertEqual(context.get("previous_url"), "/subject_listboard/19/")
        self.assertIsNone(context.get("next_url"))
        self.assertIsNone(context.get("last_url"))
        self.assertEqual(context.get("numbers")[0].number, 15)
        self.assertEqual(context.get("numbers")[-1:][0].number, 20)

    def test_page_numbers(self):
        for i in range(1, 25):
            self.assertEqual(len(page_numbers(i, 200)), 10)
            self.assertIn(i, page_numbers(i, 200))

    def test_age(self):
        context = {"reference_datetime": None}
        born = get_utcnow() - relativedelta(years=25)
        self.assertEqual(25, age_in_years(context, born))

        reference_datetime = get_utcnow() - relativedelta(years=25)
        context = {"reference_datetime": reference_datetime}
        born = reference_datetime - relativedelta(years=5)
        self.assertEqual(5, age_in_years(context, born))

        reference_datetime = get_utcnow() - relativedelta(years=25)
        context = {"reference_datetime": reference_datetime}
        born = get_utcnow()
        self.assertEqual(born, age_in_years(context, born))

    def test_human(self):
        self.assertEqual(human(11112222333344445555), "1111-2222-3333-4444-5555")
