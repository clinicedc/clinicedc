import tempfile
from pathlib import Path

from django.test import TestCase
from django.test.utils import override_settings
from edc_pdf_reports.utils import write_model_to_insecure_pdf
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_test_utils.get_user_for_tests import get_user_for_tests
from multisite import SiteID
from pypdf import PdfReader

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
from edc_lab.pdf_reports import ManifestPdfReportError


@override_settings(SITE_ID=10)
class TestManifest(SiteTestCaseMixin, TestCase):
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


@override_settings(SITE_ID=10)
class TestManifestReport(SiteTestCaseMixin, TestCase):
    def setUp(self):
        add_or_update_django_sites(single_sites=self.default_sites, verbose=False)
        self.user = get_user_for_tests(username="nchomsky")
        consignee = Consignee.objects.create(name="consignee")
        shipper = Shipper.objects.create(name="shipper")
        self.manifest = Manifest.objects.create(consignee=consignee, shipper=shipper)

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report(self):
        self.assertEqual(self.manifest.site.name, "mochudi")
        buffer = write_model_to_insecure_pdf(self.manifest, user=self.user)
        p = Path(tempfile.mkdtemp())
        q = p / "death_reports_insecure.pdf"
        q.write_bytes(buffer.getbuffer())
        reader = PdfReader(q.absolute())
        text = [page.extract_text() for page in reader.pages]
        text = " ".join(text)
        self.assertIn("mochudi", text.lower())

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report_shipped(self):
        self.manifest.shipped = True
        self.manifest.save()
        self.assertEqual(self.manifest.site.name, "mochudi")
        buffer = write_model_to_insecure_pdf(self.manifest, user=self.user)
        p = Path(tempfile.mkdtemp())
        q = p / "death_reports_insecure.pdf"
        q.write_bytes(buffer.getbuffer())
        reader = PdfReader(q.absolute())
        text = [page.extract_text() for page in reader.pages]
        text = " ".join(text)
        self.assertIn("mochudi", text.lower())

    @override_settings(SITE_ID=SiteID(default=20))
    def test_report_items_not_in_box(self):
        self.manifest.shipped = True
        self.manifest.save()
        for i in range(0, 3):
            ManifestItem.objects.create(
                manifest=self.manifest,
                identifier=f"{self.manifest.manifest_identifier}{i}",
            )
        self.assertEqual(self.manifest.site.name, "mochudi")
        self.assertRaises(
            ManifestPdfReportError, write_model_to_insecure_pdf, self.manifest, user=self.user
        )

        try:
            write_model_to_insecure_pdf(self.manifest, user=self.user)
        except ManifestPdfReportError as e:
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
        self.assertEqual(self.manifest.site.name, "mochudi")
        self.assertRaises(
            ManifestPdfReportError, write_model_to_insecure_pdf, self.manifest, user=self.user
        )
        try:
            write_model_to_insecure_pdf(self.manifest, user=self.user)
        except ManifestPdfReportError as e:
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
        self.assertEqual(self.manifest.site.name, "mochudi")
        self.assertRaises(
            ManifestPdfReportError, write_model_to_insecure_pdf, self.manifest, user=self.user
        )
        try:
            write_model_to_insecure_pdf(self.manifest, user=self.user)
        except ManifestPdfReportError as e:
            self.assertEqual(e.code, "invalid_requisition_identifier")
