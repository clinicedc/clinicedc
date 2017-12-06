from django.test import TestCase, tag

from ..templatetags.edc_dashboard_extras import paginator_row, page_numbers
from .models import TestModel
from django.core.paginator import Paginator
from pprint import pprint


class TestTags(TestCase):

    @tag('1')
    def test_(self):
        for i in range(0, 100):
            TestModel.objects.create(f1=f'object{i}')

        object_list = TestModel.objects.all()
        paginator = Paginator(object_list, 5)

        page = 1
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url='listboard_url')
        context = paginator_row(context)
        self.assertIsNone(context.get('first_url'))
        self.assertIsNone(context.get('previous_url'))
        self.assertEqual(context.get('next_url'), '/subject_listboard/2/')
        self.assertEqual(context.get('last_url'), '/subject_listboard/20/')
        self.assertEqual(context.get('numbers')[0].number, 1)
        self.assertEqual(context.get('numbers')[-1:][0].number, 10)

        page = 2
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url='listboard_url')
        context = paginator_row(context)
        self.assertEqual(context.get('first_url'), '/subject_listboard/1/')
        self.assertEqual(context.get('previous_url'), '/subject_listboard/1/')
        self.assertEqual(context.get('next_url'), '/subject_listboard/3/')
        self.assertEqual(context.get('last_url'), '/subject_listboard/20/')
        self.assertEqual(context.get('numbers')[0].number, 1)
        self.assertEqual(context.get('numbers')[-1:][0].number, 10)

        page = 3
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url='listboard_url')
        context = paginator_row(context)
        self.assertEqual(context.get('first_url'), '/subject_listboard/1/')
        self.assertEqual(context.get('previous_url'), '/subject_listboard/2/')
        self.assertEqual(context.get('next_url'), '/subject_listboard/4/')
        self.assertEqual(context.get('last_url'), '/subject_listboard/20/')
        self.assertEqual(context.get('numbers')[0].number, 1)
        self.assertEqual(context.get('numbers')[-1:][0].number, 10)

        page = 20
        context = dict(
            paginator=paginator,
            page_obj=paginator.get_page(page),
            query_string=None,
            paginator_url='listboard_url')
        context = paginator_row(context)
        pprint(context)
        self.assertEqual(context.get('first_url'), '/subject_listboard/1/')
        self.assertEqual(context.get('previous_url'), '/subject_listboard/19/')
        self.assertIsNone(context.get('next_url'))
        self.assertIsNone(context.get('last_url'))
        self.assertEqual(context.get('numbers')[0].number, 10)
        self.assertEqual(context.get('numbers')[-1:][0].number, 20)

    @tag('1')
    def test_page_numbers(self):
        for i in range(1, 25):
            self.assertEqual(len(page_numbers(i, 200)), 10)
            self.assertIn(i, page_numbers(i, 200))

    @tag('2')
    def test_page_number2s(self):
        for index, i in enumerate(range(200, 0, -1)):
            with self.subTest(index=index, i=i):
                if i >= 195:
                    self.assertEqual(
                        page_numbers(i, 200), list(range(191, 201)))
                elif i <= 5:
                    self.assertEqual(
                        page_numbers(i, 200), list(range(1, 11)))
                elif 5 < i < 195:
                    self.assertEqual(
                        page_numbers(i, 200), list(range(i - 4, i + 6)))
                else:
                    self.fail(i)
#         self.assertEqual(page_numbers(199, 200), list(range(191, 201)))
#         self.assertEqual(page_numbers(198, 200), list(range(191, 201)))
#         self.assertEqual(page_numbers(197, 200), list(range(191, 201)))
#         self.assertEqual(page_numbers(196, 200), list(range(191, 201)))
#         self.assertEqual(page_numbers(195, 200), list(range(191, 201)))
#         self.assertEqual(page_numbers(194, 200), list(range(189, 199)))
#         self.assertEqual(page_numbers(193, 200), list(range(188, 198)))
#         self.assertEqual(page_numbers(192, 200), list(range(187, 197)))
#         self.assertEqual(page_numbers(191, 200), list(range(186, 196)))
