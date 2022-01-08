from importlib import import_module

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings

from edc_list_data import LoadListDataError, site_list_data
from edc_list_data.load_model_data import LoadModelDataError
from edc_list_data.preload_data import PreloadData
from edc_list_data.site_list_data import AlreadyRegistered, SiteListDataError

from ..list_data import list_data
from ..models import (
    Antibiotic,
    Customer,
    Neurological,
    SignificantNewDiagnosis,
    Symptom,
)


class TestPreload(TestCase):
    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=True)
    def test_autodiscover_default(self):
        site_list_data.autodiscover()
        site_list_data.load_data()
        self.assertEqual(Antibiotic.objects.all().count(), 3)
        self.assertEqual(Neurological.objects.all().count(), 0)
        self.assertEqual(Symptom.objects.all().count(), 0)
        self.assertEqual(SignificantNewDiagnosis.objects.all().count(), 0)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_preload_manually(self):
        site_list_data.initialize()
        PreloadData(list_data=list_data)
        self.assertEqual(Antibiotic.objects.all().count(), 8)
        self.assertEqual(Neurological.objects.all().count(), 9)
        self.assertEqual(Symptom.objects.all().count(), 17)
        self.assertEqual(SignificantNewDiagnosis.objects.all().count(), 8)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_preload_repeat_does_not_duplicate_records(self):
        site_list_data.initialize()

        PreloadData(list_data=list_data)
        self.assertEqual(Antibiotic.objects.all().count(), 8)
        self.assertEqual(Neurological.objects.all().count(), 9)
        self.assertEqual(Symptom.objects.all().count(), 17)
        self.assertEqual(SignificantNewDiagnosis.objects.all().count(), 8)

        PreloadData(list_data=list_data)
        self.assertEqual(Antibiotic.objects.all().count(), 8)
        self.assertEqual(Neurological.objects.all().count(), 9)
        self.assertEqual(Symptom.objects.all().count(), 17)
        self.assertEqual(SignificantNewDiagnosis.objects.all().count(), 8)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_sample_app_loads(self):
        site_list_data.initialize()
        module = import_module("my_list_app.list_data")
        site_list_data.register(module)
        site_list_data.load_data()
        self.assertEqual(Antibiotic.objects.all().count(), 3)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_autodiscover_import_and_register(self):
        site_list_data.initialize()
        self.assertRaises(ModuleNotFoundError, site_list_data._import_and_register, "blah")
        site_list_data.initialize(module_name="blah")
        self.assertRaises(
            ModuleNotFoundError, site_list_data._import_and_register, app_name="my_list_app"
        )
        site_list_data.initialize(module_name="bad_list_data")
        self.assertRaises(
            SiteListDataError, site_list_data._import_and_register, app_name="my_list_app"
        )
        site_list_data.initialize(module_name="bad_list_data2")
        self.assertRaises(
            SiteListDataError, site_list_data._import_and_register, app_name="my_list_app"
        )

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_load_data(self):
        site_list_data.initialize(module_name="bad_list_data3")
        site_list_data._import_and_register(app_name="my_list_app")
        self.assertRaises(LookupError, site_list_data.load_data)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_load_model_data_no_unique_field(self):
        site_list_data.initialize(module_name="model_data")
        site_list_data._import_and_register(app_name="my_list_app")
        self.assertRaises(LoadModelDataError, site_list_data.load_data)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_load_model_data_no_unique_field2(self):
        site_list_data.initialize(module_name="model_data2")
        site_list_data._import_and_register(app_name="my_list_app")
        self.assertRaises(LoadModelDataError, site_list_data.load_data)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_load_model_data_with_unique_field(self):
        site_list_data.initialize(module_name="model_data3")
        site_list_data._import_and_register(app_name="my_list_app")
        try:
            site_list_data.load_data()
        except LoadListDataError:
            self.fail("PreloadDataError exception unexpectedly raised")

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_load_model_data_with_unique_field2(self):
        site_list_data.initialize(module_name="model_data4")
        site_list_data._import_and_register(app_name="my_list_app")
        try:
            site_list_data.load_data()
        except LoadListDataError:
            self.fail("PreloadDataError exception unexpectedly raised")

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_load_model_data_with_unique_field3(self):
        site_list_data.initialize(module_name="model_data3")
        site_list_data._import_and_register(app_name="my_list_app")
        site_list_data.load_data()
        try:
            Customer.objects.get(name="The META Trial")
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist exception unexpectedly raised")

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_sample_app_raises_on_duplicate_definition_for_table(self):
        site_list_data.initialize()
        module = import_module("my_list_app.list_data")
        site_list_data.register(module)
        module = import_module("my_list_app.dup_list_data")
        self.assertRaises(AlreadyRegistered, site_list_data.register, module)

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_edc_list_data_loads(self):
        site_list_data.initialize()
        module = import_module("edc_list_data.tests.list_data")
        site_list_data.register(module)
        self.assertIn("edc_list_data.tests.list_data", site_list_data.registry)
        self.assertIn(
            "edc_list_data.antibiotic",
            site_list_data.registry.get("edc_list_data.tests.list_data").get("list_data"),
        )

    @override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
    def test_replaced_with_definition_from_my_list_app(self):
        site_list_data.initialize()

        module = import_module("edc_list_data.tests.list_data")
        site_list_data.register(module)
        self.assertIn(
            "edc_list_data.antibiotic",
            site_list_data.registry.get("edc_list_data.tests.list_data").get("list_data"),
        )

        module = import_module("my_list_app.list_data")
        site_list_data.register(module)
        self.assertNotIn(
            "edc_list_data.antibiotic",
            site_list_data.registry.get("edc_list_data.tests.list_data").get("list_data"),
        )
        self.assertIn(
            "edc_list_data.antibiotic",
            site_list_data.registry.get("my_list_app.list_data").get("list_data"),
        )
