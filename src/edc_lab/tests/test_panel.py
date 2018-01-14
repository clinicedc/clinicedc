from django.test import TestCase, tag

from ..models import Panel
from edc_lab.site_labs import RegistryNotLoaded, site_labs
from edc_lab.lab.aliquot_type import AliquotType
from edc_lab.lab.processing_profile import ProcessingProfile
from edc_lab.lab.requisition_panel import RequisitionPanel
from edc_lab.lab.lab_profile import LabProfile
from django.core.exceptions import ObjectDoesNotExist


class TestPanel(TestCase):

    def setUp(self):
        site_labs._registry = {}

    def test_panel(self):
        Panel.objects.create(
            name='panel',
            display_name='My Panel',
            lab_profile_name='lab_profile')

    def test_panel2(self):

        wb = AliquotType(name='Whole Blood',
                         alpha_code='WB', numeric_code='02')

        whole_blood_processing = ProcessingProfile(
            name='whole_blood_store', aliquot_type=wb)

        wb_panel = RequisitionPanel(
            name='wb_storage',
            verbose_name='Whole Blood Storage',
            aliquot_type=wb,
            processing_profile=whole_blood_processing)

        lab_profile = LabProfile(
            name='test_profile',
            requisition_model='edc_lab.subjectrequisition')
        lab_profile.add_panel(wb_panel)

        site_labs.register(lab_profile=lab_profile)

        try:
            Panel.objects.get(name='wb_storage')
        except ObjectDoesNotExist:
            self.fail('Panel unexpectedly does not exist')

        panel = Panel.objects.get(name='wb_storage')

        self.assertEqual(panel.display_name, 'Whole Blood Storage')
        self.assertEqual(panel.lab_profile_name, 'test_profile')
