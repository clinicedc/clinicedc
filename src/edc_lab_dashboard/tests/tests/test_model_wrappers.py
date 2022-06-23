from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls.base import reverse
from edc_lab.models import (
    Aliquot,
    Box,
    BoxItem,
    BoxType,
    Consignee,
    Manifest,
    ManifestItem,
    Shipper,
)

from edc_lab_dashboard.model_wrappers import (
    BoxModelWrapper,
    ManageBoxItemModelWrapper,
    ManifestItemModelWrapper,
    ManifestModelWrapper,
)


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

    def test_box_model_wrapper(self):
        wrapper_cls = BoxModelWrapper
        box_type = BoxType.objects.create(across=9, down=9, total=81)
        obj = Box.objects.create(box_identifier="1234", box_type=box_type)
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href,
            f"/admin/edc_lab/box/{obj.id}/change/?"
            f"next=edc_lab_dashboard:pack_listboard_url&",
        )
        self.assertEqual(
            reverse("edc_lab_dashboard:pack_listboard_url"),
            "/edc_lab_dashboard/listboard/pack/",
        )

    def test_manage_box_item_model_wrapper(self):
        wrapper_cls = ManageBoxItemModelWrapper
        # usually this will come from app_config
        box_type = BoxType.objects.create(across=9, down=9, total=81)
        box_identifier = "1234"
        box = Box.objects.create(box_identifier=box_identifier, box_type=box_type)
        obj = BoxItem.objects.create(box=box, position=0, identifier="1234")
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href,
            f"/admin/edc_lab/boxitem/{obj.id}/change/?"
            f"next=edc_lab_dashboard:manage_box_listboard_url,"
            f"box_identifier,action_name&box_identifier={box_identifier}&"
            f"action_name=manage&",
        )

    def test_manifest_item_model_wrapper(self):
        wrapper_cls = ManifestItemModelWrapper
        manifest = Manifest.objects.create(
            site=Site.objects.get_current(),
            consignee=Consignee.objects.create(name="name"),
            shipper=Shipper.objects.create(name="name"),
        )
        obj = ManifestItem.objects.create(manifest=manifest)
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href,
            f"/admin/edc_lab/manifestitem/{obj.id}/change/?"
            f"next=edc_lab_dashboard:manage_manifest_listboard_url&",
        )

    def test_manifest_model_wrapper(self):
        wrapper_cls = ManifestModelWrapper
        obj = Manifest.objects.create(
            site=Site.objects.get_current(),
            consignee=Consignee.objects.create(name="name"),
            shipper=Shipper.objects.create(name="name"),
        )
        wrapper = wrapper_cls(obj)
        self.assertEqual(
            wrapper.href,
            f"/admin/edc_lab/manifest/{obj.id}/change/?"
            f"next=edc_lab_dashboard:manifest_listboard_url&",
        )
        self.assertEqual(
            reverse("edc_lab_dashboard:manifest_listboard_url"),
            "/edc_lab_dashboard/listboard/manifest/",
        )
