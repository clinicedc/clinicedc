import csv
from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.test import TransactionTestCase, override_settings
from edc_appointment import list_data as appointment_list_data
from edc_list_data import site_list_data
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...df_exporters import CsvNonCrfTablesExporter
from ...df_handlers import NonCrfDfHandler
from ..helper import Helper
from ..visit_schedule import get_visit_schedule

app_config = django_apps.get_app_config("edc_pdutils")


@override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False)
class TestNonCrfExporter(TransactionTestCase):
    helper = Helper()

    def setUp(self):
        self.path = mkdtemp()

    def setup_test_data(self):
        """Setup for each test"""
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(5))
        site_list_data.initialize()
        site_list_data.register(appointment_list_data, app_name="edc_appointment")
        site_list_data.load_data()
        for i in range(0, 5):
            self.helper.create_crf(i)

    def test_noncrf_tables_to_csv_from_app_label_with_columns(self):
        class MyDfHandler(NonCrfDfHandler):
            visit_tbl = "edc_pdutils_subjectvisit"
            registered_subject_tbl = "edc_registration_registeredsubject"
            appointment_tbl = "edc_appointment_appointment"

        class MyNonCsvCrfTablesExporter(CsvNonCrfTablesExporter):
            without_visit_columns = ["subject_visit_id"]
            df_handler_cls = MyDfHandler
            app_label = "edc_pdutils"
            export_folder = self.path

        self.setup_test_data()

        exporter = MyNonCsvCrfTablesExporter()
        exporter.to_csv()
        self.assertGreater(len(exporter.exported_paths), 0)
        for path in exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)
