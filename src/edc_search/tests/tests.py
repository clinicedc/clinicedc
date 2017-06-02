from django.test import TestCase, tag
from django.utils.text import slugify

from edc_base.utils import get_utcnow

from ..search_slug import SearchSlug
from .models import TestModel


class TestSearchSlug(TestCase):

    def test_search_slug_no_fields(self):
        search_slug = SearchSlug()
        self.assertEqual(search_slug.slug, '')

    def test_search_slug_with_fields(self):
        class Obj:
            f1 = 1
            f2 = 2

        search_slug = SearchSlug(
            obj=Obj(),
            fields=['f1', 'f2'])
        self.assertEqual(search_slug.slug, '1|2')

    def test_gets_slug(self):
        dt = get_utcnow()
        obj = TestModel(
            f1='erik is',
            f2=dt,
            f3=1234)
        obj.save()
        self.assertEqual(obj.slug, f'erik-is|{slugify(dt)}|1234|attr|dummy|dummy_attr')

    def test_gets_values_with_none(self):
        obj = TestModel(
            f1=None,
            f2=None,
            f3=None)
        obj.save()
        self.assertEqual(obj.slug, f'|||attr|dummy|dummy_attr')
