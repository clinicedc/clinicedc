from copy import copy

from django.test import TestCase, tag

from ..models import BasicModel


@tag("model")
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
