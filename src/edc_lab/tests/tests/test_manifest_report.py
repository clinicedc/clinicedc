from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite
from edc_sites.tests import SiteTestCaseMixin
from multisite import SiteID

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
from edc_lab.reports import ManifestReport, ManifestReportError


class TestManifest(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    settings.SITE_ID,
                    "test_site",
                    country_code="ug",
                    country="uganda",
                    domain="bugamba.ug.clinicedc.org",
                )
            ]
        )
        return super().setUpClass()

    def test_manifest(self):
        consignee = Consignee.objects.create(name="consignee")
        shipper = Shipper.objects.create(name="shipper")
        Manifest.objects.create(consignee=consignee, shipper=shipper)

    def test_manifest_with_items(self):
        consignee = Consignee.objects.create(name="consignee")
        shipper = Shipper.objects.create(name="shipper")
        manifest = Manifest.objects.create(consignee=consignee, shipper=shipper)
        ManifestItem.objects.create(manifest=manifest, identifier="aaaaaaaaaaaa")

    def test_manifest_with_items_slug(self):
        consignee = Consignee.objects.create(name="consignee")
        shipper = Shipper.objects.create(name="shipper")
        manifest = Manifest.objects.create(consignee=consignee, shipper=shipper)
        manifest_item = ManifestItem.objects.create(
            manifest=manifest, identifier="aaaaaaaaaaaabb"
        )
        self.assertIn("aaaaaaaaaaaabb", manifest_item.slug)
        self.assertIn(manifest_item.human_readable_identifier, manifest_item.slug)


class TestManifestReport(SiteTestCaseMixin, TestCase):
    def setUp(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        self.user = User.objects.create(first_name="Noam", last_name="Chomsky")
        consignee = Consignee.objects.create(name="consignee")
        shipper = Shipper.objects.create(name="shipper")
        self.manifest = Manifest.objects.create(consignee=consignee, shipper=shipper)

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report(self):
        self.assertEqual(self.manifest.site.name, "test_site")
        report = ManifestReport(manifest=self.manifest, user=self.user)
        report.render_to_response()

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report_shipped(self):
        self.manifest.shipped = True
        self.manifest.save()
        self.assertEqual(self.manifest.site.name, "test_site")
        report = ManifestReport(manifest=self.manifest, user=self.user)
        report.render_to_response()

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report_items_not_in_box(self):
        self.manifest.shipped = True
        self.manifest.save()
        for i in range(0, 3):
            ManifestItem.objects.create(
                manifest=self.manifest,
                identifier=f"{self.manifest.manifest_identifier}{i}",
            )
        self.assertEqual(self.manifest.site.name, "test_site")
        report = ManifestReport(manifest=self.manifest, user=self.user)
        self.assertRaises(ManifestReportError, report.render_to_response)
        try:
            report.render_to_response()
        except ManifestReportError as e:
            self.assertEqual(e.code, "unboxed_item")

    def test_box_type(self):
        BoxType.objects.create(name="box_type", across=8, down=8, total=64)

    def test_box(self):
        box_type = BoxType.objects.create(name="box_type", across=8, down=8, total=64)
        Box.objects.create(box_type=box_type)

    def test_box_item(self):
        box_type = BoxType.objects.create(name="box_type", across=8, down=8, total=64)
        box = Box.objects.create(box_type=box_type)
        BoxItem.objects.create(box=box, identifier=box.box_identifier, position=0)

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report_invalid_invalid_aliquot_identifier(self):
        self.manifest.shipped = True
        self.manifest.save()
        box_type = BoxType.objects.create(name="box_type", across=8, down=8, total=64)
        box = Box.objects.create(box_type=box_type)
        # add box items with invalid aliquot identifiers
        for i in range(0, 3):
            BoxItem.objects.create(box=box, identifier=f"{i}", position=i)
        ManifestItem.objects.create(manifest=self.manifest, identifier=box.box_identifier)
        self.assertEqual(self.manifest.site.name, "test_site")
        report = ManifestReport(manifest=self.manifest, user=self.user)
        self.assertRaises(ManifestReportError, report.render_to_response)
        try:
            report.render_to_response()
        except ManifestReportError as e:
            self.assertEqual(e.code, "invalid_aliquot_identifier")

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report_invalid_invalid_requisition_identifier(self):
        self.manifest.shipped = True
        self.manifest.save()
        prefix = "ABCDEFG"
        for i in range(0, 3):
            Aliquot.objects.create(count=i, aliquot_identifier=f"{prefix}{i}")
        box_type = BoxType.objects.create(name="box_type", across=8, down=8, total=64)
        box = Box.objects.create(box_type=box_type)
        # add box items with invalid aliquot identifiers
        for index, aliquot in enumerate(Aliquot.objects.all()):
            BoxItem.objects.create(
                box=box, identifier=aliquot.aliquot_identifier, position=index
            )
        ManifestItem.objects.create(manifest=self.manifest, identifier=box.box_identifier)
        self.assertEqual(self.manifest.site.name, "test_site")
        report = ManifestReport(manifest=self.manifest, user=self.user)
        self.assertRaises(ManifestReportError, report.render_to_response)
        try:
            report.render_to_response()
        except ManifestReportError as e:
            self.assertEqual(e.code, "invalid_requisition_identifier")
