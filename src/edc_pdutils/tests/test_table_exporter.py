import csv
import os
import sys

from django.apps import apps as django_apps
from django.test import TestCase, tag  # noqa
from django.db import connection

from ..csv_exporters import CsvTablesExporter
from .helper import Helper
from .visit_schedule import get_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class TestExport(TestCase):

    app_config = django_apps.get_app_config("edc_pdutils")
    path = app_config.export_folder
    helper = Helper()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(5))
        for i in range(0, 5):
            self.helper.create_crf(i)
        print("database name", connection.settings_dict["NAME"])
        # Or alternatively
        # db_name = connection.get_connection_params()['db']

    def tearDown(self):
        """Remove .csv files created in tests.
        """
        super().tearDown()
        if "edc_pdutils" not in self.path:
            raise ValueError(f"Invalid path in test. Got {self.path}")
        files = os.listdir(self.path)
        for file in files:
            if ".csv" in file:
                file = os.path.join(self.path, file)
                os.remove(file)

    @tag("1")
    def test_tables_to_csv_lower_columns(self):
        sys.stdout.write("\n")
        tables_exporter = CsvTablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                for row in csv_reader:
                    for field in row:
                        self.assertEqual(field.lower(), field)
                    break

    def test_tables_to_csv_from_app_label(self):
        sys.stdout.write("\n")
        tables_exporter = CsvTablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths.values():
            with open(path, "r") as f:
                csv_reader = csv.DictReader(f, delimiter="|")
                rows = [row for row in enumerate(csv_reader)]
            self.assertGreater(len(rows), 0)

    def test_tables_to_csv_from_app_label_exclude_history(self):
        class MyCsvTablesExporter(CsvTablesExporter):
            exclude_history_tables = True

        sys.stdout.write("\n")
        tables_exporter = MyCsvTablesExporter(app_label="edc_pdutils")
        for path in tables_exporter.exported_paths:
            self.assertNotIn("history", path)
