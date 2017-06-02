from django.test.testcases import TestCase

from edc_base.utils import get_utcnow

from .models import TestModel


class TestSearchSlug(TestCase):

    def test_gets_values(self):
        dt = get_utcnow()
        obj = TestModel(
            f1='erik is',
            f2=dt,
            f3=1234)
        self.assertEqual(obj.get_search_slug_values(), ['erik is', dt, 1234])

    def test_gets_slug(self):
        dt = get_utcnow()
        obj = TestModel(
            f1='erik is',
            f2=dt,
            f3=1234)
        self.assertTrue(obj.get_search_slug())

    def test_gets_values_with_none(self):
        obj = TestModel(
            f1=None,
            f2=None,
            f3=None)
        obj.slug
        self.assertEqual(obj.get_search_slug_values(), [None, None, None])

    def test_gets_slug_with_none(self):
        obj = TestModel(
            f1=None,
            f2=None,
            f3=None)
        obj.slug
        self.assertEqual(obj.get_search_slug(), '||')
