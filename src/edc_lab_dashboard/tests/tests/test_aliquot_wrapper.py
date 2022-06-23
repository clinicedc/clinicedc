from copy import copy

from django.apps import apps as django_apps
from django.test import TestCase
from edc_lab.models import Aliquot, Box, BoxItem, BoxType

from edc_lab_dashboard.model_wrappers import AliquotModelWrapper

app_config = django_apps.get_app_config("edc_lab_dashboard")


class TestModelWrapper(TestCase):
    def setUp(self):
        self.box_type = BoxType.objects.create(name="9 x 9", across=9, down=9, total=81)
        self.box = Box.objects.create(box_identifier="12345678", box_type=self.box_type)
        self.box_item = BoxItem.objects.create(box=self.box, position=0)
        self.aliquot = Aliquot.objects.create(
            subject_identifier="ABCDEFG",
            count=1,
            is_primary=True,
            aliquot_type="Whole Blood",
            numeric_code="02",
            alpha_code="WB",
        )
        self.wrapper_cls = AliquotModelWrapper

    def test_aliquot_model_wrapper(self):
        wrapper = self.wrapper_cls(self.aliquot)
        self.assertEqual(
            wrapper.href,
            f"/admin/edc_lab/aliquot/{self.aliquot.id}/change/?"
            f"next=edc_lab_dashboard:aliquot_listboard_url&",
        )
        self.assertIn("edc_lab_dashboard:aliquot_listboard_url", wrapper.href)

    def test_aliquot_wrapper_attrs(self):
        """Asserts attrs used in template exist."""
        wrapper = self.wrapper_cls(self.aliquot)
        attrs = [
            "is_primary",
            "box_item",
            "manifest_item",
            "subject_identifier",
            "aliquot_datetime",
            "aliquot_type",
            "numeric_code",
            "alpha_code",
            "box_item",
            "shipped",
            "count",
        ]
        for attr in attrs:
            with self.subTest(attr=attr):
                self.assertTrue(hasattr(wrapper, attr))

    def test_aliquot_wrapper_attrs2(self):
        wrapper = self.wrapper_cls(self.aliquot)
        self.assertTrue(wrapper.human_readable_identifier)
        self.assertTrue(wrapper.is_primary)
        self.assertTrue(wrapper.box_item)
        self.assertTrue(wrapper.box_item.box.box_identifier)
        self.assertTrue(wrapper.box_item.box.get_category_display)
        self.assertTrue(wrapper.box_item.box.box_identifier)
        self.assertTrue(wrapper.subject_identifier)
        self.assertTrue(wrapper.aliquot_datetime)
        self.assertTrue(wrapper.aliquot_type)
        self.assertTrue(wrapper.numeric_code)
        self.assertTrue(wrapper.alpha_code)
        self.assertTrue(wrapper.box_item)
        self.assertTrue(wrapper.count)
        self.assertIsNone(wrapper.manifest_item)
        self.assertFalse(wrapper.shipped)

    def test_aliquot_wrapper_attrs3(self):
        aliquot = copy(self.aliquot)
        wrapper = self.wrapper_cls(aliquot)
        self.box_item.delete()
        self.assertIsNone(wrapper.box_item)

        aliquot = copy(self.aliquot)
        wrapper = self.wrapper_cls(aliquot)
        self.assertIsNone(wrapper.box_item)
