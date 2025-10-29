from clinicedc_constants import NULL_STRING
from clinicedc_tests.models import TestModelSlug, TestModelSlugExtra
from django.db import models
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_search.generate_slug import generate_slug
from edc_search.model_mixins import SearchSlugModelMixin


@tag("search")
@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=False,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestSearchSlug(TestCase):
    def test_search_slug_no_fields(self):
        self.assertIsNone(generate_slug(None, None))

    def test_search_slug_with_fields(self):
        class MyModel(SearchSlugModelMixin, models.Model):
            f1 = models.IntegerField(default=1)
            f2 = models.IntegerField(default=2)

        slug = generate_slug(obj=MyModel(), fields=("f1", "f2"))
        self.assertEqual(slug, "")

    def test_gets_slug(self):
        dt = timezone.now()
        obj = TestModelSlug(f1="erik is", f2=dt, f3=1234)
        obj.save()
        self.assertEqual(
            sorted(obj.slug.split("|")), sorted(["dummy_attr", "attr", "erik-is"])
        )

    def test_gets_with_none(self):
        obj = TestModelSlug(f1="", f2=None, f3=None)
        obj.save()
        self.assertEqual(sorted(obj.slug.split("|")), sorted(["dummy_attr", "attr"]))

    def test_gets_with_inherit(self):
        obj = TestModelSlugExtra(
            f1="i am from testmodel", f2=None, f3=None, f4="i am from testmodelextra"
        )
        obj.save()

        self.assertEqual(
            sorted(obj.slug.split("|")),
            sorted(["dummy_attr", "attr", "i-am-from-testmodel", "i-am-from-testmodelextra"]),
        )

    def test_updater(self):
        obj = TestModelSlug.objects.create(f1="x" * 300)
        obj.save()
        obj.refresh_from_db()
        obj.slug = NULL_STRING
        obj.save()
        obj.refresh_from_db()
        self.assertIsNotNone(obj.slug)
        TestModelSlug.objects.update_search_slugs()
        obj = TestModelSlug.objects.all()[0]
        self.assertIsNotNone(obj.slug)
