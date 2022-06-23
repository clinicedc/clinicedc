from django.apps import apps as django_apps
from django.test import TestCase
from edc_lab.models import Aliquot, Box, BoxType
from edc_lab.models.box_item import BoxItem

from edc_lab_dashboard.model_wrappers import BoxModelWrapper

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

        self.wrapper_cls = BoxModelWrapper
        box_type = BoxType.objects.create(across=9, down=9, total=81)
        self.box = Box.objects.create(box_identifier="1234", box_type=box_type)

    def test_box_model_wrapper_href(self):
        wrapper = self.wrapper_cls(self.box)
        self.assertEqual(
            wrapper.href,
            f"/admin/edc_lab/box/{self.box.id}/change/?"
            f"next=edc_lab_dashboard:pack_listboard_url&",
        )

    def test_box_model_wrapper_template_attrs(self):
        wrapper = self.wrapper_cls(self.box)
        attrs = ["human_readable_identifier", "comment", "created", "user_created"]
        for attr in attrs:
            with self.subTest(attr=attr):
                self.assertTrue(hasattr(wrapper, attr))
