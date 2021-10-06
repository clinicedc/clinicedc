import re

from django.conf import settings
from django.test import TestCase
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite

from edc_lab.identifiers import RequisitionIdentifier
from edc_lab.lab import (
    AliquotType,
    LabProfile,
    Process,
    ProcessingProfile,
    RequisitionPanel,
)
from edc_lab.site_labs import site_labs


class TestRequisition(TestCase):
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

    def test_requisition_identifier(self):
        """Asserts requisition identifier class creates identifier
        with correct format.
        """
        identifier = RequisitionIdentifier()
        pattern = re.compile("[0-9]{2}[A-Z0-9]{5}")
        self.assertTrue(pattern.match(str(identifier)))


class TestRequisitionModel(TestCase):
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

    def setUp(self):
        self.requisition_model = "edc_lab.subjectrequisition"
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(name="Viral Load", processing_profile=processing_profile)
        self.lab_profile = LabProfile(name="profile", requisition_model=self.requisition_model)
        self.lab_profile.add_panel(panel)
        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=self.lab_profile)

    def test_(self):
        obj = site_labs.get(lab_profile_name="profile")
        self.assertEqual(obj, self.lab_profile)

    def test_lab_profile_model(self):
        obj = site_labs.get(lab_profile_name="profile")
        self.assertEqual(self.requisition_model, obj.requisition_model)

    def test_panel_model(self):
        for panel in site_labs.get(lab_profile_name="profile").panels.values():
            self.assertEqual(panel.requisition_model, self.requisition_model)
