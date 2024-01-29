from copy import copy

from django.test import TestCase

from edc_model.models import UrlModelMixinNoReverseMatch

from ..models import BasicModel, SimpleModel


class TestModels(TestCase):
    def test_base_update_fields(self):
        """Assert update fields cannot bypass modified fields."""
        obj = BasicModel.objects.create()
        modified = copy(obj.modified)

        obj.save(update_fields=["f1"])
        obj.refresh_from_db()

        self.assertNotEqual(modified, obj.modified)

    def test_base_verbose_name(self):
        obj = BasicModel.objects.create()
        self.assertEqual(obj.verbose_name, obj._meta.verbose_name)

    def test_get_absolute_url_change(self):
        obj = BasicModel.objects.create()
        self.assertEqual(
            obj.get_absolute_url(), f"/admin/edc_model/basicmodel/{str(obj.id)}/change/"
        )

    def test_get_absolute_url_add(self):
        obj = BasicModel()
        self.assertEqual(obj.get_absolute_url(), "/admin/edc_model/basicmodel/add/")

    def test_get_absolute_url_not_registered(self):
        obj = SimpleModel()
        self.assertRaises(UrlModelMixinNoReverseMatch, obj.get_absolute_url)
