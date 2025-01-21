from django.test import TestCase
from edc_lab.models import Box, BoxItem, BoxType

from edc_lab_dashboard.templatetags.edc_lab_extras import verified


class TestTemplateTags(TestCase):
    def test_verified(self):
        box_type, _ = BoxType.objects.get_or_create(name="9 x 9", across=9, down=9, total=81)
        box = Box.objects.create(box_identifier="12345678", box_type=box_type)
        box_item, _ = BoxItem.objects.get_or_create(box=box, position=0, identifier="1")
        self.assertEqual(verified(box_item), "")
        box_item, _ = BoxItem.objects.get_or_create(
            box=box, position=2, identifier="2", verified=True
        )
        self.assertIn("verified", verified(box_item))
