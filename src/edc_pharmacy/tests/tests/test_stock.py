from django.db.models.signals import pre_save
from django.test import TestCase, override_settings
from edc_facility import import_holidays
from edc_list_data import site_list_data
from edc_pdutils.helper import Helper


@override_settings(SUBJECT_CONSENT_MODEL="edc_pharmacy.subjectconsent", SITE_ID=1)
class TestMedicationCrf(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")

    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()

    def test_ok(self):
        pass
