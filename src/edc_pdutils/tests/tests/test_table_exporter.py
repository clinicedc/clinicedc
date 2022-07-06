import csv
import os

from django.apps import apps as django_apps
from django.test import TestCase
from edc_facility import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...df_exporters import TablesExporter
from ..helper import Helper
from ..visit_schedule import get_visit_schedule


class TestExport(TestCase):

    app_config = django_apps.get_app_config("edc_pdutils")
    path = app_config.export_folder
    helper = Helper()

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(5))
        for i in range(0, 5):
            self.helper.create_crf(i)

    def tearDown(self):
        """Remove .csv files created in tests."""
        super().tearDown()
        if "edc_pdutils" not in self.path:
            raise ValueError(f"Invalid path in test. Got {self.path}")
        files = os.listdir(self.path)
        for file in files:
            if ".csv" in file:
                file = os.path.join(self.path, file)
                os.remove(file)

    def test_tables_to_csv_lower_columns(self):
        tables_exporter = TablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                for row in csv_reader:
                    for field in row:
                        self.assertEqual(field.lower(), field)
                    break

    def test_tables_to_csv_from_app_label(self):
        tables_exporter = TablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)

    def test_tables_to_csv_from_app_label_exclude_history(self):
        class MyTablesExporter(TablesExporter):
            exclude_history_tables = True

        tables_exporter = MyTablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths:
            self.assertNotIn("history", path)
