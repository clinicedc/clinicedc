import re

from django.test import TestCase, override_settings, tag

from edc_facility.import_holidays import import_holidays
from edc_lab.identifiers import RequisitionIdentifier
from edc_lab.site_labs import site_labs
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from tests.labs import lab_profile
from tests.sites import all_sites


@tag("lab")
@override_settings(SITE_ID=10)
class TestRequisitionModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.requisition_model = "tests.subjectrequisition"
        site_labs.initialize()
        site_labs.register(lab_profile=lab_profile)

    def test_requisition_identifier(self):
        """Asserts requisition identifier class creates identifier
        with correct format.
        """
        identifier = RequisitionIdentifier()
        pattern = re.compile("[0-9]{2}[A-Z0-9]{5}")
        self.assertTrue(pattern.match(str(identifier)))

    def test_(self):
        obj = site_labs.get(lab_profile_name="lab_profile")
        self.assertEqual(obj, lab_profile)

    def test_lab_profile_model(self):
        obj = site_labs.get(lab_profile_name="lab_profile")
        self.assertEqual(self.requisition_model, obj.requisition_model)

    def test_panel_model(self):
        for panel in site_labs.get(lab_profile_name="lab_profile").panels.values():
            self.assertEqual(panel.requisition_model, self.requisition_model)
